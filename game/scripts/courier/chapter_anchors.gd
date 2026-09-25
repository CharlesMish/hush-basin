extends "res://scripts/courier/narrative_anchors.gd"
## Sparse chapter presentation. No collision, steering, cameras or rig animation.
var south: Node3D
var unpacked: Node3D
var jackets: Node3D
var hanging: Node3D
var repair_bag: Node3D
var apron_stack: Node3D
var parts_case: Node3D
var mail: Node3D
var patch: Node3D
var scuff: Node3D
var mending_signs: Array[Label3D]=[]

func configure_chapter(data: P1AWorldData,craft: CraftController) -> void:
	super.configure(data)
	parts_case=Node3D.new();relay.add_child(parts_case)
	_box(parts_case,Vector3(1.0,1.25,0),Vector3(.55,.35,.6),Color("a28e68"))
	mail=Node3D.new();relay.add_child(mail)
	for i in 3:_box(mail,Vector3(-1.15,1.1+i*.04,.18),Vector3(.5,.04,.45),Color("d5c5a0"))
	south=_anchor(data,"TES",Vector2(0,6),"TESS · SOUTH COUNTER")
	for child in south.get_children():
		if child is Label3D:child.position.y=3.2
	_box(south,Vector3(0,1.05,0),Vector3(4,.16,1.25),Color("77624e"))
	for x in [-1.7,1.7]:_box(south,Vector3(x,.52,0),Vector3(.16,1.04,1.0),Color("485453"))
	# The counter remains below the existing north frontage, outside its plinth.
	_box(south,Vector3(0,2.75,.45),Vector3(4.5,.16,1.7),Color("69453b"))
	for x in [-2.1,2.1]:_box(south,Vector3(x,1.4,.65),Vector3(.12,2.8,.12),Color("485453"))
	for x in [-2.75,2.75]:
		for y in [.3,.8]:_box(south,Vector3(x,y,.2),Vector3(1.1,.1,.9),Color("626650"))
	_label(south,"IN",Vector3(-2.75,1.2,.25),.008);_label(south,"OUT",Vector3(2.75,1.2,.25),.008)
	unpacked=Node3D.new();south.add_child(unpacked)
	_box(unpacked,Vector3(-2.1,.35,-1),Vector3(.85,.7,.75),Color("a08b67"))
	_box(unpacked,Vector3(-2.1,.78,-1.28),Vector3(.85,.06,.45),Color("baa17b"))
	jackets=Node3D.new();south.add_child(jackets)
	for i in 3:_box(jackets,Vector3(.2,1.2+i*.12,0),Vector3(1.1,.1,.65),Color("687774"))
	hanging=Node3D.new();south.add_child(hanging)
	_box(hanging,Vector3(0,2.3,.45),Vector3(3.5,.06,.06),Color("bdab8c"))
	for x in [-1.2,0,1.2]:
		_box(hanging,Vector3(x,1.8,.45),Vector3(.62,.9,.06),Color("bbb08e"));_box(hanging,Vector3(x,2.07,.45),Vector3(.95,.23,.06),Color("bbb08e"))
	repair_bag=Node3D.new();south.add_child(repair_bag)
	_box(repair_bag,Vector3(-2.75,1.1,.2),Vector3(.65,.5,.55),Color("9a9d8a"));_box(repair_bag,Vector3(-2.75,1.36,.2),Vector3(.08,.03,.58),Color("6b96aa"))
	var depot:=_anchor(data,"DEP",Vector2(5,-4),"FREIGHT RECEIVING")
	_box(depot,Vector3(0,.9,0),Vector3(2.5,.14,1.1),Color("776a51"))
	for x in [-1,1]:_box(depot,Vector3(x,.43,0),Vector3(.12,.86,.8),Color("4b5552"))
	apron_stack=Node3D.new();depot.add_child(apron_stack)
	for i in 3:_box(apron_stack,Vector3(0,1.02+i*.09,0),Vector3(.8,.08,.7),Color("d0c4a3"))
	# The current native sign is TEA & REPAIRS, despite a later unused data label.
	# Adapt only its two B11 labels in this scene; preserve baked geometry.
	for n in get_parent().find_children("*","Label3D",true,false):
		if n.text=="TEA & REPAIRS" and Vector2(n.global_position.x,n.global_position.z).distance_to(Vector2(40,95))<20:
			n.text="TEA &"
			var sign:=Label3D.new();sign.text="MENDING";sign.font_size=n.font_size;sign.pixel_size=n.pixel_size;sign.outline_size=0
			n.get_parent().add_child(sign);sign.transform=n.transform
			var left_width: float=ThemeDB.fallback_font.get_string_size("TEA & ",HORIZONTAL_ALIGNMENT_LEFT,-1,n.font_size).x*n.pixel_size
			var right_width: float=ThemeDB.fallback_font.get_string_size("MENDING",HORIZONTAL_ALIGNMENT_LEFT,-1,n.font_size).x*n.pixel_size
			sign.position+=n.basis.x*(left_width*.5);n.position-=n.basis.x*(right_width*.5)
			sign.no_depth_test=false;mending_signs.append(sign)
	# Existing rigid rear inner leaf: top plane y=.028, usable x=.03..44,z=±.20.
	# Child geometry follows the authored rig; no rig source or pose is modified.
	var leaf: Node3D=craft.get_node("VisualRoot/RearStarboardRig/SocketSlide/YawPivot/HaunchPivot/InnerLeaf")
	patch=Node3D.new();patch.name="TessPanelPatch";leaf.add_child(patch)
	_box(patch,Vector3(.30,.032,.08),Vector3(.23,.006,.27),Color("c4a57d"))
	for z in [-.025,.025,.075,.125,.175]:
		for x in [.205,.395]:_box(patch,Vector3(x,.036,z),Vector3(.025,.002,.012),Color("713f35"))
	scuff=Node3D.new();leaf.add_child(scuff)
	for i in 3:_box(scuff,Vector3(.37-i*.018,.030,.06+i*.036),Vector3(.095,.002,.013),Color("86968b"))

func _label(parent: Node3D,text: String,at: Vector3,size: float) -> Label3D:
	var label:=Label3D.new();label.text=text;label.position=at;label.font_size=40;label.pixel_size=size;label.billboard=BaseMaterial3D.BILLBOARD_ENABLED;parent.add_child(label);return label
func update_chapter(r: Dictionary) -> void:
	var step:=int(r.step)
	super.update_state(2 if step>=3 else 1 if step>=2 else 0,r.parcel,step>=4,r.pending)
	parts_case.visible=step<=1 and r.parcel!="relay_stock";mail.visible=step>=1
	jackets.visible=step<5 and r.parcel!="tess_jackets";apron_stack.visible=step<6 and r.parcel!="tess_aprons"
	unpacked.visible=step<7;hanging.visible=step>=7;repair_bag.visible=step>=7
	patch.visible=r.patch;scuff.visible=not r.patch
	for sign in mending_signs:sign.modulate=Color("ffd799") if step>=7 else Color("827b69")
