extends RefCounted
## Optional route execution only. No craft, cargo, BRRR or world writes.
## Named road geometry comes from the retained authoritative route bake.
const Contacts=preload("res://scripts/courier/cargo_observer.gd")
const ENTRY_DEPTH:=8.0
const SWEEP_TARGET_S:=10.0
const ROUTE_SAMPLE_STRIDE:=16 # ~4 m; curvature radii are 42 m or larger.
var routes: Dictionary={}
var objective:=""
var phase:=0
var active:=false
var complete:=false
var elapsed:=0.0
var best_sweep_s:=-1.0
var progress_m:=0.0
var reason:="ready"
var armed:=true
var last_position:=Vector3.ZERO
var initialized:=false
var snapshot: Dictionary={}

func configure(data: P1AWorldData) -> void:
 for id in ["A1","A2","X0"]:
  var raw: Array=data.routes[id].points_xz_m
  var points: Array[Vector2]=[]
  for index in range(0,raw.size(),ROUTE_SAMPLE_STRIDE):points.append(P1AWorldData.xz(raw[index]))
  var last:=P1AWorldData.xz(raw[-1])
  if points[-1]!=last:points.append(last)
  var reverse_route: bool=id!="A1"
  if reverse_route:points.reverse()
  var arcs: Array[float]=[0.0]
  for index in range(1,points.size()):arcs.append(arcs[-1]+points[index-1].distance_to(points[index]))
  var definition: Dictionary=data.manifest.routes[id]
  var from_node: String=definition.to_node if reverse_route else definition.from_node
  var to_node: String=definition.from_node if reverse_route else definition.to_node
  # Named junction edges bound the measured road section. Broad existing
  # forecourts remain free for braking and choosing the next road.
  routes[id]={"points":points,"arcs":arcs,"length":arcs[-1],"width":float(definition.operational_half_width_m),"start":float(data.manifest.junctions[from_node].radius_m),"end":arcs[-1]-float(data.manifest.junctions[to_node].radius_m)}

func begin(kind: String,position: Vector3) -> void:
 objective=kind;phase=0;active=false;complete=false;elapsed=0;best_sweep_s=-1
 progress_m=0;reason="ready";armed=true;last_position=position;initialized=true;snapshot={}

func sample(craft: CraftController,dt: float) -> Dictionary:
 if not initialized:begin(objective,craft.global_position)
 var moved:=craft.global_position.distance_to(last_position)
 var discontinuity:=moved>maxf(3.0,craft.velocity.length()*dt*3.0)
 last_position=craft.global_position
 var contacts:=Contacts.contacts(craft)
 return step(Vector2(last_position.x,last_position.z),dt,bool(contacts.wall_touch),discontinuity)

func step(p: Vector2,dt: float,wall: bool,discontinuity: bool) -> Dictionary:
 if objective not in ["SWEEP","HAUL"]:return _snapshot()
 if complete:return _snapshot()
 var id: String="A1" if objective=="SWEEP" else "A2" if phase==0 else "X0"
 var route: Dictionary=routes[id]
 var projection:=project(route,p)
 var at_entry: bool=float(projection.distance)<=float(route.width) and float(projection.along)>=float(route.start) and float(projection.along)<=float(route.start)+ENTRY_DEPTH
 if not at_entry:armed=true
 if not active and armed and at_entry:
  active=true;armed=false;elapsed=0;progress_m=0;reason="running"
 if active:
  elapsed+=dt;progress_m=maxf(progress_m,float(projection.along))
  var outside: bool=float(projection.distance)>float(route.width)
  var clean_required:=objective=="HAUL" and phase==1
  if discontinuity or outside or (clean_required and wall):
   active=false;reason="reset" if discontinuity else "left road" if outside else "Shelf contact"
  elif float(projection.along)>=float(route.end):
   active=false
   if objective=="SWEEP":
    best_sweep_s=elapsed if best_sweep_s<0 else minf(best_sweep_s,elapsed)
    complete=elapsed<=SWEEP_TARGET_S+0.000000001
    reason="complete" if complete else "over reference"
   elif phase==0:
    phase=1;armed=true;progress_m=0;reason="Shelf ready"
   else:phase=2;complete=true;reason="complete"
 return _snapshot()

func _snapshot() -> Dictionary:
 snapshot={"route_objective":objective,"route_phase":phase,"route_active":active,"route_complete":complete,"route_elapsed_s":elapsed,"route_progress_m":progress_m,"route_reason":reason,"best_sweep_s":best_sweep_s}
 return snapshot

static func project(route: Dictionary,p: Vector2) -> Dictionary:
 var best:=INF
 var along:=0.0
 var points: Array=route.points
 var arcs: Array=route.arcs
 for i in range(1,points.size()):
  var segment: Vector2=points[i]-points[i-1]
  var fraction:=clampf((p-points[i-1]).dot(segment)/segment.length_squared(),0,1)
  var d:=p.distance_squared_to(points[i-1]+segment*fraction)
  if d<best:
   best=d;along=float(arcs[i-1])+segment.length()*fraction
 return {"distance":sqrt(best),"along":along}
