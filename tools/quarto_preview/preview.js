import { Engine } from '/engine/Engines/engine.js';
import { Scene } from '/engine/scene.js';
import { ArcRotateCamera } from '/engine/Cameras/arcRotateCamera.js';
import { Vector3, Quaternion } from '/engine/Maths/math.vector.js';
import { Color3, Color4 } from '/engine/Maths/math.color.js';
import { Mesh } from '/engine/Meshes/mesh.js';
import { TransformNode } from '/engine/Meshes/transformNode.js';
import { VertexData } from '/engine/Meshes/mesh.vertexData.js';
import { StandardMaterial } from '/engine/Materials/standardMaterial.js';
import { HemisphericLight } from '/engine/Lights/hemisphericLight.js';
import { DirectionalLight } from '/engine/Lights/directionalLight.js';
import { CreateGround } from '/engine/Meshes/Builders/groundBuilder.js';
import '/engine/Shaders/default.vertex.js';
import '/engine/Shaders/default.fragment.js';

const byId = id => document.getElementById(id);
const stage = (start, end, value) => {
  const t = Math.max(0, Math.min(1, (value - start) / Math.max(end - start, 0.0001)));
  return t * t * (3 - 2 * t);
};
const mix = (a, b, t) => a.map((v, i) => v + (b[i] - v) * t);
const scale = (a, s) => a.map(v => v * s);
const color = value => Color3.FromArray(value);
const vec = value => Vector3.FromArray(value);
const radians = value => value * Math.PI / 180;

try {
  const [data, tuning] = await Promise.all([
    fetch('/vehicle.json').then(r => { if (!r.ok) throw new Error('Canonical geometry missing'); return r.json(); }),
    fetch('/camera.json').then(r => r.json()),
  ]);
  const engine = new Engine(byId('renderCanvas'), true, { preserveDrawingBuffer: true, stencil: true });
  engine.setHardwareScalingLevel(Math.max(1, window.devicePixelRatio / 1.5));
  const scene = new Scene(engine);
  scene.useRightHandedSystem = true;
  scene.clearColor = new Color4(0.075, 0.097, 0.104, 1);
  const camera = new ArcRotateCamera('inspection', 1.1, 1.05, 4.6, new Vector3(0, 0.2, 0), scene);
  camera.minZ = 0.01;
  camera.maxZ = 100;
  camera.lowerRadiusLimit = 0.65;
  camera.upperRadiusLimit = 24;
  camera.wheelDeltaPercentage = 0.012;
  camera.panningSensibility = 1500;
  camera.attachControl(byId('renderCanvas'), true);
  const ambient = new HemisphericLight('overcast fill', new Vector3(0.2, 1, -0.25), scene);
  ambient.intensity = 0.95;
  ambient.diffuse = new Color3(0.80, 0.86, 0.88);
  ambient.groundColor = new Color3(0.31, 0.30, 0.26);
  const sun = new DirectionalLight('warm key', new Vector3(-0.35, -0.9, 0.45), scene);
  sun.diffuse = new Color3(1, 0.91, 0.77);
  sun.intensity = 0.9;
  const ground = CreateGround('review ground (not game world)', { width: 40, height: 40 }, scene);
  ground.position.y = -0.50;
  const groundMaterial = new StandardMaterial('review ground', scene);
  groundMaterial.diffuseColor = new Color3(0.16, 0.17, 0.16);
  groundMaterial.specularColor = Color3.Black();
  ground.material = groundMaterial;
  const sourceMaterials = new Map();
  for (const [id, spec] of Object.entries(data.materials)) {
    const material = new StandardMaterial(id, scene);
    material.diffuseColor = color(spec.albedo_color ?? [0.5, 0.5, 0.5]);
    material.alpha = (spec.albedo_color ?? [1, 1, 1, 1])[3] ?? 1;
    material.specularColor = color([1, 1, 1].map(() => 0.16 + (spec.metallic ?? 0) * 0.3));
    material.specularPower = 16 + (1 - (spec.roughness ?? 0.5)) * 80;
    material.emissiveColor = spec.emission_enabled === false ? Color3.Black() : color(scale((spec.emission ?? [0, 0, 0]).slice(0, 3), spec.emission_energy_multiplier ?? 1));
    sourceMaterials.set(id, material);
  }
  const nodes = new Map();
  const rest = new Map();
  const energyPaths = new Set(data.energy_material_paths ?? []);
  const propulsionPaths = new Set(data.propulsion_material_paths ?? []);
  let triangleCount = 0;
  for (const spec of data.nodes) {
    let node;
    if (spec.mesh) {
      node = new Mesh(spec.path, scene);
      const source = data.meshes[spec.mesh];
      if (!source) throw new Error(`Unknown mesh ${spec.mesh}`);
      const vertices = new VertexData();
      vertices.positions = source.vertices.flat();
      vertices.normals = source.normals.flat();
      // Godot authors clockwise front faces; convert to the conventional
      // counterclockwise winding used by this right-handed Babylon scene.
      vertices.indices = source.indices.slice();
      for (let i = 0; i < vertices.indices.length; i += 3) {
        [vertices.indices[i + 1], vertices.indices[i + 2]] = [vertices.indices[i + 2], vertices.indices[i + 1]];
      }
      vertices.applyToMesh(node);
      node.material = sourceMaterials.get(spec.material);
      if (energyPaths.has(spec.path) || propulsionPaths.has(spec.path)) {
        node.material = node.material.clone(`${spec.path}:energy`);
      }
      triangleCount += source.indices.length / 3;
    } else {
      node = new TransformNode(spec.path, scene);
    }
    node.metadata = { canonicalPath: spec.path, canonicalMesh: spec.mesh ?? null };
    nodes.set(spec.path, node);
    rest.set(spec.path, {
      position: (spec.position ?? [0, 0, 0]).slice(),
      rotation_degrees: (spec.rotation_degrees ?? [0, 0, 0]).slice(),
    });
  }
  for (const spec of data.nodes) {
    if (spec.parent && spec.parent !== '.') {
      const parent = nodes.get(spec.parent);
      if (!parent) throw new Error(`Missing parent ${spec.parent} for ${spec.path}`);
      nodes.get(spec.path).parent = parent;
    }
  }
  let amount = 0;
  let selectedView = 'orbit';
  let playing = false;
  let direction = 1;
  let hold = 0;
  let framingFactor = 1;
  const desiredFramingFactor = () => Math.max(1, 1.3 / engine.getAspectRatio(camera));
  const materialsByRole = role => [...role].map(path => nodes.get(path)?.material).filter(Boolean);
  const energyMaterials = materialsByRole(energyPaths);
  const propulsionMaterials = materialsByRole(propulsionPaths);

  function applyPose(value) {
    amount = Math.max(0, Math.min(1, value));
    const posed = new Map([...rest].map(([path, spec]) => [path, { position: spec.position.slice(), rotation_degrees: spec.rotation_degrees.slice() }]));
    for (const channel of data.pose_channels) {
      const target = posed.get(channel.path);
      if (!target) throw new Error(`Missing pose node ${channel.path}`);
      target[channel.property][channel.component] += channel.travel * stage(channel.start, channel.end, amount);
    }
    for (const [path, spec] of posed) {
      const node = nodes.get(path);
      node.position.copyFrom(vec(spec.position));
      const [x, y, z] = spec.rotation_degrees.map(radians);
      // Godot Node3D's default YXZ Euler order: Y * X * Z.
      node.rotationQuaternion = Quaternion.RotationYawPitchRoll(y, x, z);
    }
    const colors = data.energy_colors ?? {};
    const spread = colors.SPREAD ?? [1, 0.58, 0.16];
    const drive = colors.DRIVE ?? [0.2, 0.95, 1];
    const caution = colors.CAUTION ?? [1, 0.72, 0.12];
    const strike = colors.STRIKE ?? [1, 0.12, 0.08];
    const state = byId('energy').value;
    const current = (state === 'CAUTION' ? caution : state === 'STRIKE' ? strike : mix(spread, drive, amount)).slice(0, 3);
    for (const material of energyMaterials) {
      material.diffuseColor = color(current);
      material.emissiveColor = color(scale(current, 0.58 * (0.7 + 0.65 * amount)));
    }
    const propulsion = stage(...(data.propulsion_window ?? [0.88, 1]), amount);
    for (const material of propulsionMaterials) {
      material.diffuseColor = color(mix(current, [1, 1, 1], 0.18));
      material.emissiveColor = color(scale(current, 0.82 * (0.22 + 1.23 * propulsion)));
    }
    byId('scrub').value = String(amount);
    byId('amount').value = `${Math.round(amount * 100)}%`;
    if (selectedView === 'game') camera.fov = radians(tuning.spread_camera_fov + tuning.drive_fov_increase * amount);
  }

  function setView(view) {
    selectedView = view;
    camera.fov = radians(42);
    camera.setTarget(new Vector3(0, 0.17, 0));
    if (view === 'game') {
      camera.setTarget(new Vector3(0, tuning.camera_look_height, -tuning.camera_look_ahead));
      camera.setPosition(new Vector3(0, tuning.camera_height, tuning.camera_distance));
      camera.fov = radians(tuning.spread_camera_fov + tuning.drive_fov_increase * amount);
    } else if (view === 'side') {
      camera.setPosition(new Vector3(4.6, 0.65, 0));
    } else if (view === 'stern') {
      camera.setTarget(new Vector3(0, 0.1, 0.35));
      camera.setPosition(new Vector3(0.7, 0.7, 3.6));
    } else {
      camera.setPosition(new Vector3(2.2, 1.67, 2.67));
    }
    framingFactor = view === 'game' ? 1 : desiredFramingFactor();
    camera.radius *= framingFactor;
    byId('viewLabel').textContent = { game: 'Game camera · stationary, unobstructed frame', side: 'Side · folio and body relationship', stern: 'Stern · fixed core and moving hollow can', orbit: 'Inspection orbit' }[view];
    document.querySelectorAll('[data-view]').forEach(button => button.setAttribute('aria-pressed', String(button.dataset.view === view)));
  }

  function stop() {
    playing = false;
    byId('play').textContent = 'Play';
  }
  byId('scrub').addEventListener('input', event => { stop(); applyPose(Number(event.target.value)); });
  byId('spread').addEventListener('click', () => { stop(); applyPose(0); });
  byId('drive').addEventListener('click', () => { stop(); applyPose(1); });
  byId('energy').addEventListener('change', () => applyPose(amount));
  byId('play').addEventListener('click', () => {
    playing = !playing;
    direction = amount >= 1 ? -1 : 1;
    hold = 0;
    byId('play').textContent = playing ? 'Pause' : 'Play';
  });
  document.querySelectorAll('[data-view]').forEach(button => button.addEventListener('click', () => setView(button.dataset.view)));
  window.addEventListener('resize', () => {
    engine.resize();
    if (selectedView !== 'game') {
      const next = desiredFramingFactor();
      camera.radius *= next / framingFactor;
      framingFactor = next;
    }
  });
  let previousTime = performance.now();
  engine.runRenderLoop(() => {
    const now = performance.now();
    const delta = (now - previousTime) / 1000;
    previousTime = now;
    if (playing) {
      if (hold > 0) hold -= delta;
      else {
        const duration = byId('speed').value === 'slow' ? 4 : direction > 0 ? tuning.fold_duration : tuning.deploy_duration;
        applyPose(amount + direction * delta / duration);
        if (amount === 0 || amount === 1) { direction *= -1; hold = 0.85; }
      }
    }
    scene.render();
  });
  const meshCount = data.nodes.filter(node => node.mesh).length;
  byId('status').textContent = `${meshCount} native mesh instances · ${triangleCount.toLocaleString()} triangles · ${data.pose_channels.length} shared pose channels · source: game/presentation/quarto_native_v1.json`;
  applyPose(0);
  setView('orbit');
  await scene.whenReadyAsync();
  // Read-only observation plus explicit preview controls for reproducible capture.
  window.__QUARTO_PREVIEW = {
    getState: () => ({ amount, view: selectedView, energy: byId('energy').value, meshCount, triangleCount, channelCount: data.pose_channels.length, renderer: 'Babylon geometry preview; not native Godot evidence', playing }),
    setPose: value => { stop(); applyPose(value); },
    setView,
    getNodeTransforms: () => [...nodes].map(([path, node]) => ({ path, position: node.position.asArray(), rotation: node.rotationQuaternion.asArray(), world: Array.from(node.computeWorldMatrix(true).asArray()) })),
  };
} catch (error) {
  byId('error').style.display = 'block';
  byId('error').textContent = String(error.stack ?? error);
  byId('status').textContent = 'Geometry preview failed to load; see the error above.';
  console.error(error);
}
