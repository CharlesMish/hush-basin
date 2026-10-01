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
const Slice=preload("res://scripts/courier/slices_text.gd")
var market_visit:=""
var sleeve_bench: Node3D
var sleeve_initial: Node3D
var sleeve_red: Node3D
var held_sleeve: Node3D
var unrolled_sleeve: Node3D
var folded_red: Node3D
var pads: Node3D
var handling_card: Node3D
var plain_word: Label3D
var red_word: Label3D
var strike: MeshInstance3D
var never_line: Label3D
var mending_label: Node3D
var routed_parcel: Node3D
var stool: Node3D
var busy_orders: Node3D
var corner_saucer: Node3D
var interrupted_plate: Node3D
var market_note: Node3D
var thread_box: Node3D
var relay_tray: Node3D
var pinned_letter: Node3D

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
	configure_third_chapter()

func configure_third_chapter() -> void:
	sleeve_bench=Node3D.new();quarry.add_child(sleeve_bench);sleeve_bench.position=Vector3(5.2,0,-1.4)
	_box(sleeve_bench,Vector3(0,1.02,0),Vector3(3.6,.17,1.5),Color("8b795f"))
	for x in [-1.45,1.45]:_box(sleeve_bench,Vector3(x,.5,0),Vector3(.2,1,1.2),Color("53665f"))
	sleeve_initial=sleeve(sleeve_bench,false,true);sleeve_initial.position.y=1.17
	sleeve_red=sleeve(sleeve_bench,true,false);sleeve_red.position.y=1.14
	pads=Node3D.new();sleeve_bench.add_child(pads)
	for x in [-.7,.7]:
		_box(pads,Vector3(x,1.2,0),Vector3(.8,.2,.8),Color("817b5d"))
		_box(pads,Vector3(x,1.32,0),Vector3(.15,.035,.95),Color("554e3d"))
	_box(pads,Vector3(.7,1.35,.1),Vector3(.45,.02,.42),Color("dfd0ae"))
	handling_card=Node3D.new();sleeve_bench.add_child(handling_card)
	_box(handling_card,Vector3(0,2.65,-.4),Vector3(5.0,2.65,.09),Color("d6c9a8"))
	card_text(handling_card,"SLEEVES —",Vector3(0,3.64,-.34),.011)
	plain_word=card_text(handling_card,"PLAIN",Vector3(0,2.73,-.33),.011)
	card_text(handling_card,"SIDE TO THE STONE",Vector3(0,2.20,-.33),.010)
	red_word=card_text(handling_card,"RED",Vector3(0,3.17,-.31),.010)
	strike=_box(handling_card,Vector3(0,2.73,-.28),Vector3(1.35,.045,.015),Color("504b40"));strike.rotation.z=.10
	never_line=card_text(handling_card,"NEVER DOWN ON ITS FACE",Vector3(0,1.67,-.31),.009)
	# Tess's retained outer cloth has one sound patch. Red is a whole flat lining.
	unrolled_sleeve=sleeve(south,false,false);unrolled_sleeve.position=Vector3(0,1.17,0)
	folded_red=sleeve(south,true,true);folded_red.position=Vector3(0,1.55,-.12);folded_red.rotation.x=-.6
	held_sleeve=sleeve(south,false,true);held_sleeve.position=Vector3(1.25,2.12,.53);held_sleeve.rotation.x=PI/2
	_box(south,Vector3(1.25,2.63,.5),Vector3(.1,.28,.32),Color("374b47"))
	stool=make_stool(south,Vector3(.7,0,-1.8))
	mending_label=Node3D.new();south.add_child(mending_label)
	mending_label.position.x=-.55
	_box(mending_label,Vector3(-2.75,1.82,.12),Vector3(3.8,1.10,.07),Color("d6c9a8"))
	var label:=card_text(mending_label,"MENDING —\nTAGGED, PLEASE",Vector3(-2.75,1.83,.06),.013);label.rotation.y=PI
	routed_parcel=Node3D.new();south.add_child(routed_parcel)
	_box(routed_parcel,Vector3(-2.75,1.12,-.03),Vector3(.75,.48,.6),Color("9e8766"))
	_box(routed_parcel,Vector3(-2.75,1.37,-.03),Vector3(.1,.03,.62),Color("d8ccb0"))
	_box(routed_parcel,Vector3(-2.42,1.26,-.36),Vector3(.3,.24,.03),Color("e3d8b8"))
	make_stool(market,Vector3(.75,.45,-.82))
	busy_orders=Node3D.new();market.add_child(busy_orders)
	for x in [-1.3,0,1.3]:_box(busy_orders,Vector3(x,1.38,0),Vector3(.8,.3,.55),Color("c6b99b"))
	corner_saucer=Node3D.new();market.add_child(corner_saucer)
	corner_saucer.position.y=.45
	_box(corner_saucer,Vector3(.75,.83,-.82),Vector3(.65,.045,.55),Color("e4d7b9"))
	_box(corner_saucer,Vector3(.75,.91,-.82),Vector3(.32,.13,.28),Color("664530"))
	interrupted_plate=Node3D.new();market.add_child(interrupted_plate)
	interrupted_plate.position.y=.45
	_box(interrupted_plate,Vector3(.75,.84,-.82),Vector3(.82,.05,.65),Color("e4d7b9"))
	_box(interrupted_plate,Vector3(.7,.93,-.87),Vector3(.32,.13,.24),Color("664530"))
	_box(interrupted_plate,Vector3(.63,.93,-.71),Vector3(.17,.13,.1),Color("664530"))
	_box(interrupted_plate,Vector3(.9,.89,-.74),Vector3(.055,.035,.51),Color("b9bdb2"))
	for x in [.84,.9,.96]:_box(interrupted_plate,Vector3(x,.9,-1.05),Vector3(.028,.02,.16),Color("b9bdb2"))
	market_note=Node3D.new();market.add_child(market_note)
	_box(market_note,Vector3(-.65,1.25,0),Vector3(.5,.02,.4),Color("e7d8b7"))
	thread_box=Node3D.new();relay.add_child(thread_box)
	_box(thread_box,Vector3(2.3,1.0,0),Vector3(.9,.48,.7),Color("947b5a"))
	for x in [2.05,2.3,2.55]:_box(thread_box,Vector3(x,1.29,0),Vector3(.17,.16,.3),Color("b7a98c"))
	_box(thread_box,Vector3(2.3,1.4,0),Vector3(.52,.03,.4),Color("e7d8b7"))
	relay_tray=Node3D.new();relay.add_child(relay_tray)
	_box(relay_tray,Vector3(2.3,.86,0),Vector3(1,.12,.75),Color("7d8981"))
	_box(relay_tray,Vector3(2.3,.94,0),Vector3(.42,.02,.35),Color("e0d1b0"))
	pinned_letter=Node3D.new();relay.add_child(pinned_letter)
	_box(pinned_letter,Vector3(1.85,1.85,-.25),Vector3(.48,.65,.035),Color("e0d1b0"))
	_box(pinned_letter,Vector3(1.85,2.10,-.21),Vector3(.055,.055,.03),Color("905f43"))

func sleeve(parent: Node3D,red: bool,folded: bool) -> Node3D:
	var root:=Node3D.new();parent.add_child(root)
	var size:=Vector3(2.8,.12,1.0) if not folded else Vector3(2.4,.23,1.2 if red else .76)
	_box(root,Vector3.ZERO,size,Color("827967"))
	if folded and not red:
		var roll:=MeshInstance3D.new();var mesh:=CylinderMesh.new();mesh.top_radius=.25;mesh.bottom_radius=.25;mesh.height=2.4;roll.mesh=mesh;roll.rotation.z=PI/2;roll.position=Vector3(0,.23,-.06);roll.material_override=_material(Color("827967"));root.add_child(roll)
	# A single, uninterrupted canvas working plane; no raised stripe or seam.
	_box(root,Vector3(0,size.y*.5+.007,-.04),Vector3(size.x-.10,.014,size.z-.18),Color("ac4b3b") if red else Color("827967"))
	_box(root,Vector3(-size.x*.5+.3,-size.y*.5-.013 if red else size.y*.5+.020,size.z*.5-.11),Vector3(.40,.02,.20),Color("9c8d70"))
	if not red:
		for x in [-.6,-.23,.12,.47]:_box(root,Vector3(x,size.y*.5+.017,-.12),Vector3(.065,.02,.045),Color("494b40"))
	_box(root,Vector3(-size.x*.5+.28,size.y*.5+.055,size.z*.5+.07),Vector3(.36,.015,.25),Color("dfd1af"))
	return root
func card_text(parent: Node3D,text: String,at: Vector3,size: float) -> Label3D:
	var label:=_label(parent,text,at,size);label.billboard=BaseMaterial3D.BILLBOARD_DISABLED;label.modulate=Color("353f39");label.outline_size=0
	return label
func make_stool(parent: Node3D,at: Vector3) -> Node3D:
	var root:=Node3D.new();parent.add_child(root);root.position=at
	_box(root,Vector3(0,.72,0),Vector3(.9,.12,.7),Color("947955"))
	for x in [-.34,.34]:_box(root,Vector3(x,.35,0),Vector3(.10,.7,.52),Color("657166"))
	return root

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
	update_third_chapter(r)

func update_third_chapter(r: Dictionary) -> void:
	var s: Dictionary=r.slices;var done: Array=s.done
	var started:=Slice.chapter_two_complete(r)
	sleeve_bench.visible=started
	sleeve_initial.visible=not "quarry_sleeve" in done and r.parcel!="quarry_sleeve"
	sleeve_red.visible="relined_sleeve" in done
	pads.visible="quarry_sleeve" in done and not "kneeling_pads" in done and r.parcel!="kneeling_pads"
	plain_word.visible=true;red_word.visible="relined_sleeve" in done;strike.visible=red_word.visible;never_line.visible=red_word.visible
	unrolled_sleeve.visible=r.pending=="tess_sleeve"
	held_sleeve.visible="quarry_sleeve" in done and not s.relined and not unrolled_sleeve.visible
	folded_red.visible=s.relined and not "relined_sleeve" in done and r.parcel!="relined_sleeve"
	# The new held sleeve replaces the apron display only in this authored slice.
	if "quarry_sleeve" in done:hanging.visible=false
	mending_label.visible=s.shelf_label;routed_parcel.visible="tagged_mending" in done
	if routed_parcel.visible:repair_bag.visible=false
	stool.visible=started
	var busy: bool=r.parcel=="tray_one" or market_visit=="tray_one"
	var interrupted: bool=r.parcel=="tray_two" or market_visit=="tray_two" or r.pending=="nell_interruption"
	busy_orders.visible=busy;corner_saucer.visible=busy;interrupted_plate.visible=interrupted
	market_note.visible=interrupted and r.pending!="nell_interruption" and r.parcel!="tray_two"
	hatch.position.y=2.42 if interrupted else 2.95;hatch.scale.y=4.5 if interrupted else 1.0
	thread_box.visible="tray_two" in done and not "thread_box" in done and r.parcel!="thread_box"
	relay_tray.visible=started and not "tray_two" in done and not r.parcel in ["tray_one","tray_two"]
	pinned_letter.visible="ren_letter" in done
