extends "res://scripts/courier/chapter_anchors.gd"
## Authored physical evidence only; no collision bodies or camera control.
var quarry: Node3D
var clinic: Node3D
var market: Node3D
var new_stone: Node3D
var folded_tarp: Node3D
var open_tarp: Node3D
var clinic_old: Node3D
var clinic_new: Node3D
var clinic_pad: Node3D
var clinic_released: Node3D
var released_supports: Node3D
var clinic_cart: Node3D
var quarry_blocks: Node3D
var quarry_bedded: Node3D
var rut: Node3D
var barrow: Node3D
var market_crate: Node3D
var meal: Node3D
var hatch: MeshInstance3D
var meal_visit:=false

func configure_chapter(data: P1AWorldData,craft: CraftController) -> void:
	super.configure_chapter(data,craft)
	quarry=_anchor(data,"QRY",Vector2(-9,0),"QUARRY STORES");quarry.rotation.y=PI/2
	clinic=_anchor(data,"CLN",Vector2(8,6),"CLINIC RECEIVING");clinic.rotation.y=atan2(-8.0,-6.0)
	for root in [quarry,clinic]:
		# Ground-level receiving door: a small open bay, outside the old raised facades.
		_box(root,Vector3(-2.1,1.7,-.75),Vector3(1,3.4,2),Color("747a70"))
		_box(root,Vector3(2.1,1.7,-.75),Vector3(1,3.4,2),Color("747a70"))
		_box(root,Vector3(0,3.35,-.75),Vector3(5.3,.25,2.4),Color("5e645f"))
		_box(root,Vector3(0,1.45,-1.7),Vector3(3.2,2.9,.12),Color("333e3c"))
		_box(root,Vector3(0,.05,-.95),Vector3(3.2,.1,1.5),Color("7d7d6e"))
		_box(root,Vector3(-1.52,1.45,.15),Vector3(.12,2.9,.12),Color("a9a78f"))
	# The shared construction preserves the old slab's dish and track spacing.
	clinic_old=threshold(clinic,false,false);clinic_new=threshold(clinic,true,false)
	clinic_pad=threshold(clinic,true,false);clinic_pad.position=Vector3(4,.18,1.0)
	for x in [3,5]:_box(clinic,Vector3(x,.09,1),Vector3(.3,.18,1.9),Color("9f8660"))
	clinic_released=threshold(clinic,false,false);clinic_released.position=Vector3(-3.8,.85,-.3);clinic_released.rotation.x=1.1
	released_supports=Node3D.new();clinic.add_child(released_supports)
	for x in [-4.8,-2.8]:_box(released_supports,Vector3(x,.12,.1),Vector3(.35,.24,1.0),Color("a58b66"))
	clinic_cart=cart(clinic,false)
	var pallet:=Node3D.new();quarry.add_child(pallet);pallet.position=Vector3(4.5,0,1)
	for x in [-1.35,0,1.35]:_box(pallet,Vector3(x,.15,0),Vector3(.25,.3,1.8),Color("8b7356"))
	for z in [-.65,-.22,.22,.65]:_box(pallet,Vector3(0,.32,z),Vector3(3.7,.12,.38),Color("a38b67"))
	new_stone=threshold(pallet,true,false);new_stone.position.y=.4
	open_tarp=Node3D.new();pallet.add_child(open_tarp)
	_box(open_tarp,Vector3(1.0,.7,0),Vector3(1.65,.12,1.85),Color("667574"))
	for z in [-.45,.4]:_box(open_tarp,Vector3(1.15,.77,z),Vector3(.52,.02,.45),Color("b59774"))
	folded_tarp=Node3D.new();pallet.add_child(folded_tarp)
	_box(folded_tarp,Vector3(1.05,.5,0),Vector3(.9,.22,.8),Color("667574"))
	_box(folded_tarp,Vector3(1.05,.62,.08),Vector3(.4,.02,.35),Color("b59774"))
	rut=Node3D.new();quarry.add_child(rut)
	_box(rut,Vector3(.67,.025,.8),Vector3(.46,.025,3.4),Color("484b3f"))
	for x in [.35,.96]:_box(rut,Vector3(x,.07,.8),Vector3(.14,.09,3.4),Color("7b7766"))
	quarry_blocks=threshold(quarry,false,false);quarry_blocks.position=Vector3(-4,.4,.5)
	for x in [-1,1]:_box(quarry_blocks,Vector3(x,-.2,0),Vector3(.38,.4,1.8),Color("a58b66"))
	quarry_bedded=threshold(quarry,false,true)
	barrow=cart(quarry,true);barrow.position=Vector3(.65,.31,-.1)
	# Rope on its hook remains through both versions of the doorway.
	var coil:=MeshInstance3D.new();var ring:=TorusMesh.new();ring.inner_radius=.30;ring.outer_radius=.40;coil.mesh=ring;coil.rotation.x=PI/2;coil.position=Vector3(2.15,1.65,.35);coil.material_override=_material(Color("a79165"));quarry.add_child(coil)
	_box(quarry,Vector3(2.15,2.08,.35),Vector3(.07,.28,.28),Color("394b4b"))
	market=_anchor(data,"MRK",Vector2(6,-7),"MARKET HATCH")
	_box(market,Vector3(0,.55,-.7),Vector3(4.5,1.1,.18),Color("677b71"))
	for x in [-2.1,2.1]:_box(market,Vector3(x,1.7,-.7),Vector3(.2,3.4,.3),Color("526b62"))
	_box(market,Vector3(0,3.25,-.7),Vector3(4.6,.2,1.8),Color("596e64"))
	_box(market,Vector3(0,1.15,0),Vector3(4.5,.15,1.2),Color("ab9474"))
	hatch=_box(market,Vector3(0,2.95,-.6),Vector3(4.1,.3,.12),Color("667c71"))
	market_crate=Node3D.new();market.add_child(market_crate)
	_box(market_crate,Vector3(0,.3,.1),Vector3(1.7,.6,1),Color("8d795b"))
	_box(market_crate,Vector3(0,.62,.1),Vector3(1.45,.04,.8),Color("444d46"))
	_label(market_crate,"RETURNS",Vector3(0,.65,.62),.006)
	meal=Node3D.new();market.add_child(meal)
	_box(meal,Vector3(-1.0,1.33,0),Vector3(.8,.2,.55),Color("bca17b"))
	_box(meal,Vector3(-1.0,1.44,0),Vector3(.04,.02,.59),Color("58534b"))
	_box(meal,Vector3(-.8,1.47,.1),Vector3(.3,.025,.25),Color("e5d6b4"))
	_box(meal,Vector3(.8,1.31,-.4),Vector3(.85,.14,.6),Color("555b56"))
	for x in [.52,.8,1.08]:_box(meal,Vector3(x,1.42,-.4),Vector3(.23,.14,.48),Color("805736"))
	_box(meal,Vector3(1.55,1.27,.05),Vector3(.5,.045,.5),Color("e2d5b7"))
	_box(meal,Vector3(1.55,1.36,.05),Vector3(.28,.14,.28),Color("64462f"))

func threshold(parent: Node3D,pale: bool,sawn: bool) -> Node3D:
	var root:=Node3D.new();parent.add_child(root)
	var body:=Color("c9c4ac") if pale else Color("696e69")
	_box(root,Vector3(0,.08,0),Vector3(3.4,.16,1.7),body.darkened(.12))
	# Longitudinal strips with a lowered center make the wear a silhouette, not a decal.
	for i in 20:
		var x: float=-1.7+(i+.5)*.17
		var top: float=.28 if pale else .40-.24*pow(1.0-absf(x)/1.7,2)
		var color:=body
		if not pale:color=body.darkened(.14*(1.0-absf(x)/1.7))
		if not pale and (absf(x-.68)<.14 or absf(x+.68)<.14):color=Color("b8b9a8")
		_box(root,Vector3(x,(top+.14)*.5,0),Vector3(.17,top-.14,1.7),color)
	if pale:
		# Shallow approach bevel, flat working face and no door-side lip.
		var bevel:=_box(root,Vector3(0,.10,.91),Vector3(3.4,.15,.28),body);bevel.rotation.x=-.35
	else:
		_box(root,Vector3(0,.26 if sawn else .40,-.77),Vector3(3.4,.08 if sawn else .28,.25),Color("d3ccb6") if sawn else body.darkened(.17))
	return root
func cart(parent: Node3D,one_wheel: bool) -> Node3D:
	var root:=Node3D.new();parent.add_child(root)
	_box(root,Vector3(0,.75,0),Vector3(1.15,.15,1.1),Color("84928a"))
	if one_wheel:
		for x in [-.57,.57]:_box(root,Vector3(x,.98,0),Vector3(.1,.4,1.15),Color("697f73"))
	else:
		_box(root,Vector3(0,1.25,0),Vector3(1.15,.1,1.1),Color("a6afa0"))
		for x in [-.48,.48]:_box(root,Vector3(x,.88,-.4),Vector3(.05,.8,.05),Color("52655c"))
	for x in ([0] if one_wheel else [-.46,.46]):
		for z in ([-.55] if one_wheel else [-.42,.42]):
			var wheel:=MeshInstance3D.new();var mesh:=CylinderMesh.new();mesh.top_radius=.30 if one_wheel else .16;mesh.bottom_radius=mesh.top_radius;mesh.height=.12;wheel.mesh=mesh;wheel.rotation.z=PI/2;wheel.position=Vector3(x,mesh.top_radius,z);wheel.material_override=_material(Color("3c4743"));root.add_child(wheel)
	for x in [-.45,.45]:_box(root,Vector3(x,.9,.9),Vector3(.09,.09,1.2),Color("887554"))
	return root
func update_chapter(r: Dictionary) -> void:
	super.update_chapter(r)
	if quarry==null:return
	var s: Dictionary=r.slices
	var loaded: bool=r.parcel=="new_threshold" or "new_threshold" in s.done
	new_stone.visible=not loaded;open_tarp.visible=not loaded;folded_tarp.visible=loaded
	clinic_old.visible=not s.installed;clinic_new.visible=s.installed
	clinic_pad.visible="new_threshold" in s.done and not s.installed
	clinic_released.visible=s.installed and not "old_threshold" in s.done and r.parcel!="old_threshold"
	released_supports.visible=clinic_released.visible
	clinic_cart.position=Vector3(0,.28,-.6 if s.installed else -.11)
	quarry_blocks.visible="old_threshold" in s.done and not s.bedded
	quarry_bedded.visible=s.bedded;barrow.visible=s.bedded;rut.visible=not s.bedded
	# Wheel scuffs belong only to the installed pale face.
	if s.installed and not clinic_new.has_node("Scuffs"):
		var scuffs:=Node3D.new();scuffs.name="Scuffs";clinic_new.add_child(scuffs)
		for x in [-.46,.46]:_box(scuffs,Vector3(x,.284,0),Vector3(.07,.008,1.65),Color("9b9e92"))
	market_crate.visible="nell_first_tray" in s.done or r.parcel=="nell_first_tray"
	meal.visible=meal_visit or r.parcel=="nell_first_tray"
