extends SceneTree
const Execution=preload("res://scripts/courier/route_execution.gd")
var checks: Array=[]
var data:=P1AWorldData.new()
func _initialize() -> void:call_deferred("run")
func check(id: String,ok: bool) -> void:checks.append({"id":id,"pass":ok})
func observer(kind: String) -> RefCounted:
 var result:=Execution.new();result.configure(data);result.begin(kind,Vector3.ZERO);return result
func point(route: Dictionary,along: float) -> Vector2:
 for i in range(1,route.points.size()):
  if float(route.arcs[i])>=along:
   var f: float=(along-float(route.arcs[i-1]))/(float(route.arcs[i])-float(route.arcs[i-1]))
   return route.points[i-1].lerp(route.points[i],f)
 return route.points[-1]
func traverse(o: RefCounted,id: String,duration: float,wall_tick: int=-1,reverse: bool=false) -> void:
 var route: Dictionary=o.routes[id]
 var steps:=600
 for i in range(steps+1):
  var fraction:=float(i)/steps
  if reverse:fraction=1-fraction
  var p:=point(route,lerpf(float(route.start),float(route.end)+.1,fraction))
  o.step(p,0.0 if i==0 else duration/steps,i==wall_tick,false)
func run() -> void:
 check("source_world_valid",data.load_all())
 var o=observer("SWEEP")
 check("sweep_start_is_existing_GW_radius",o.routes.A1.start==float(data.manifest.junctions.GW.radius_m))
 check("sweep_end_is_existing_RLY_radius",is_equal_approx(o.routes.A1.length-o.routes.A1.end,float(data.manifest.junctions.RLY.radius_m)))
 check("corridors_are_authoritative_operational_widths",o.routes.A1.width==17 and o.routes.A2.width==17 and o.routes.X0.width==12)
 traverse(o,"A1",9.5);check("complete_section_below_reference",o.complete)
 o=observer("SWEEP");traverse(o,"A1",10.5);check("slow_section_does_not_complete",not o.complete and o.best_sweep_s>10)
 o=observer("SWEEP");traverse(o,"A1",10.0);check("exact_reference_inclusive",o.complete)
 o=observer("SWEEP");traverse(o,"A1",9.5,250);check("express_does_not_claim_collision_purity",o.complete)
 o=observer("SWEEP");traverse(o,"A1",9.5,-1,true);check("reverse_visit_does_not_complete",not o.complete)
 o=observer("SWEEP")
 for i in 600:o.step(Vector2(0,20-i*.4),1.0/60,false,false)
 check("straight_interior_never_starts_sweep",not o.complete and o.best_sweep_s<0)
 var route: Dictionary=o.routes.A1
 o.step(point(route,route.start),0,false,false)
 o.step(Vector2(500,500),.1,false,false)
 o.step(point(route,route.end),.1,false,false)
 check("leave_road_cannot_join_at_end",not o.complete and o.reason=="left road")
 traverse(o,"A1",9.5);check("return_to_entry_can_retry",o.complete)
 o=observer("SWEEP");o.step(point(route,route.start),0,false,false);o.step(point(route,route.end),.1,false,true)
 check("diagnostic_relocation_cannot_complete",not o.complete and o.reason=="reset")
 o=observer("HAUL");traverse(o,"X0",35);check("shelf_alone_not_haul",not o.complete and o.phase==0)
 traverse(o,"A2",20);check("east_approach_earns_first_phase",o.phase==1 and not o.complete)
 traverse(o,"X0",43);check("full_clean_shelf_completes_haul",o.complete and o.phase==2)
 var saved: Dictionary=o.snapshot.duplicate()
 o.step(Vector2.ZERO,1,true,true);check("earned_objective_remains_earned",o.complete and o.snapshot==saved)
 o=observer("HAUL");traverse(o,"A2",20,100);check("east_approach_is_geographic_not_care_gate",o.phase==1)
 traverse(o,"X0",43,250);check("shelf_wall_contact_breaks_crossing",not o.complete and o.phase==1 and o.reason=="Shelf contact")
 var shelf: Dictionary=o.routes.X0
 o.step(point(shelf,shelf.end),.1,false,false);check("later_shelf_tail_cannot_repair_broken_crossing",not o.complete)
 traverse(o,"X0",43);check("clean_shelf_retry_keeps_earned_east_approach",o.complete)
 o=observer("HAUL");traverse(o,"A2",40);traverse(o,"X0",80);check("no_hidden_haul_timeout_or_form_requirement",o.complete)
 o=observer("CARE");o.step(Vector2.ZERO,100,true,false);check("other_objectives_untouched",not o.complete and not o.active and o.elapsed==0)
 var failed:=0
 for row in checks:
  if not row["pass"]:failed+=1
 var result:={"passed":checks.size()-failed,"total":checks.size(),"failed":failed,"checks":checks,"scope":"Pure observer predicates; full driving trials are separate evidence."}
 var args:=OS.get_cmdline_user_args()
 if "--output" in args:FileAccess.open(args[args.find("--output")+1],FileAccess.WRITE).store_string(JSON.stringify(result,"  "))
 print("MASTERY_ROUTE_PREDICATES ",JSON.stringify(result));quit(0 if failed==0 else 1)
