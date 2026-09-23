extends Node3D
## Presentation only. No collision, camera writes or player-control reads.
var incoming: Node3D
var finished: Node3D
var installed: Node3D
var arriving: Node3D
var indicator: MeshInstance3D
var outbound: Node3D
var works: Node3D
var relay: Node3D

func configure(data: P1AWorldData) -> void:
	works=_anchor(data,"WRK",Vector2(5,-4),"WORKS FABRICATION — Ivo")
	relay=_anchor(data,"RLY",Vector2(5,-4),"RELAY DISPATCH — Ren")
	for root in [works,relay]:
		_box(root,Vector3(0,1,0),Vector3(3.2,.16,1.2),Color("555951"))
		for x in [-1.35,1.35]:_box(root,Vector3(x,.47,0),Vector3(.14,.94,.8),Color("39474a"))
		_box(root,Vector3(0,2.2,-.45),Vector3(3,.08,.16),Color("e9c085"),true)
	# Chair and crate stay modest and occupied throughout this first test.
	_box(works,Vector3(2.4,.52,0),Vector3(.8,.12,.8),Color("7e6e53"))
	_box(works,Vector3(2.4,1,.35),Vector3(.8,.9,.10),Color("7e6e53"))
	for x in [2.1,2.7]:_box(works,Vector3(x,.25,0),Vector3(.09,.5,.65),Color("434d4c"))
	_box(works,Vector3(2.4,.89,0),Vector3(.78,.62,.65),Color("535c54"))
	incoming=Node3D.new();works.add_child(incoming)
	_box(incoming,Vector3(-.65,1.26,0),Vector3(.8,.4,.65),Color("a08c66"))
	_box(incoming,Vector3(-.65,1.49,0),Vector3(.65,.06,.5),Color("bbc4ba"))
	_box(incoming,Vector3(.5,1.4,0),Vector3(.75,.55,.5),Color("55777a"))
	finished=_receiver(works);installed=_receiver(relay)
	arriving=_receiver(relay);arriving.position=Vector3(0,0,.65)
	_box(relay,Vector3(-.3,1.62,-.38),Vector3(1.8,1,.14),Color("465659"))
	indicator=_box(relay,Vector3(1.25,1.35,.1),Vector3(.22,.22,.14),Color("deb174"),true)
	_box(relay,Vector3(2.3,.7,0),Vector3(1.1,.12,1),Color("686957"))
	_box(relay,Vector3(2.3,.3,0),Vector3(1.1,.12,1),Color("686957"))
	outbound=Node3D.new();relay.add_child(outbound)
	_box(outbound,Vector3(2.3,.97,0),Vector3(.8,.45,.65),Color("ad9574"))
	_box(outbound,Vector3(2.3,1.20,0),Vector3(.12,.02,.67),Color("d1c3a4"))

func update_state(stage: int,parcel: String,done: bool,pending: String="") -> void:
	incoming.visible=stage==0
	finished.visible=stage==1 and parcel!="relay_receiver"
	installed.visible=stage==2;indicator.visible=stage==2
	arriving.visible=pending=="relay"
	outbound.visible=stage==2 and parcel!="relay_quarry" and not done

func _anchor(data: P1AWorldData,id: String,offset: Vector2,title: String) -> Node3D:
	var p:=P1AWorldData.xz(data.manifest.destination_pads[id].center_xz_m)+offset
	var root:=Node3D.new();root.position=Vector3(p.x,data.terrain_height_at(p.x,p.y),p.y);add_child(root)
	var plaque:=Label3D.new();plaque.text=title;plaque.font_size=48;plaque.pixel_size=.008;plaque.position=Vector3(0,2.65,0);plaque.billboard=BaseMaterial3D.BILLBOARD_ENABLED;plaque.no_depth_test=false;root.add_child(plaque)
	return root

func _receiver(root: Node3D) -> Node3D:
	var r:=Node3D.new();root.add_child(r)
	_box(r,Vector3(-.3,1.48,0),Vector3(1.6,.75,.55),Color("55777a"))
	_box(r,Vector3(-.75,1.5,.3),Vector3(.4,.45,.035),Color("354446"))
	var dial:=MeshInstance3D.new();var mesh:=CylinderMesh.new();mesh.top_radius=.25;mesh.bottom_radius=.25;mesh.height=.14;mesh.radial_segments=16;dial.mesh=mesh;dial.rotation_degrees.x=90;dial.position=Vector3(.15,1.5,.36);dial.material_override=_material(Color("d7b882"));r.add_child(dial)
	_box(r,Vector3(.15,1.6,.45),Vector3(.045,.17,.02),Color("3b4b4c"))
	return r

func _box(root: Node3D,at: Vector3,size: Vector3,color: Color,lit: bool=false) -> MeshInstance3D:
	var n:=MeshInstance3D.new();var mesh:=BoxMesh.new();mesh.size=size;n.mesh=mesh;n.position=at;n.material_override=_material(color,lit);root.add_child(n);return n

func _material(color: Color,lit: bool=false) -> StandardMaterial3D:
	var m:=StandardMaterial3D.new();m.albedo_color=color;m.roughness=.85
	if lit:m.emission_enabled=true;m.emission=color;m.emission_energy_multiplier=.65
	return m
