extends Node3D

# Eye position is measured inside the canopy, relative to the car body.
const EYE := Vector3(-.315,1.12,.65)
const STEERING_AXIS := Vector3(0,.235,1)
var race
var wheel: MeshInstance3D
var cluster_surface: MeshInstance3D
var mirror_surface: MeshInstance3D
var nav_surface: MeshInstance3D
var cluster: SubViewport
var navigator: SubViewport
var map_readout: Control
var rear_view: SubViewport
var rear_camera: Camera3D
var readout: Control
var cabin_light: OmniLight3D
var last_speed := 0.0
var fore_aft := 0.0
var lateral := 0.0
var sleeves:Array[MeshInstance3D]=[]
var rest_sleeves:Array[Transform3D]=[]

func prepare(circuit):
    race=circuit
    for part in race.body.find_children("*","MeshInstance3D",true,false):
        part.layers=3
    var trim:MeshInstance3D=race.body.find_child("CabinTrim",true,false)
    wheel=race.body.find_child("SteeringWheel",true,false)
    cluster_surface=race.body.find_child("InstrumentDisplay",true,false)
    mirror_surface=race.body.find_child("MirrorDisplay",true,false)
    nav_surface=race.body.find_child("RouteDisplay",true,false)
    for name_hint in ["SleeveL","SleeveR"]:
        var sleeve:MeshInstance3D=race.body.find_child(name_hint,true,false)
        sleeves.append(sleeve)
        rest_sleeves.append(sleeve.transform)
    for part: MeshInstance3D in [trim,wheel,cluster_surface,mirror_surface,nav_surface]+sleeves:
        part.layers=8
        part.cast_shadow=GeometryInstance3D.SHADOW_CASTING_SETTING_OFF
    race.body.find_child("OuterCanopy",true,false).layers=6
    race.camera.set_cull_mask_value(2,false)
    if DisplayServer.get_name()!="headless":
        cluster=SubViewport.new()
        cluster.size=Vector2i(730,200)
        cluster.disable_3d=true
        add_child(cluster)
        readout=preload("res://scripts/dash_readout.gd").new()
        readout.race=race
        readout.size=Vector2(cluster.size)
        cluster.add_child(readout)
        bind_screen(cluster_surface,cluster,false)
        navigator=SubViewport.new()
        navigator.size=Vector2i(428,274)
        navigator.disable_3d=true
        add_child(navigator)
        map_readout=preload("res://scripts/instruments.gd").new()
        map_readout.map_only=true
        map_readout.race=race
        map_readout.size=Vector2(214,137)
        map_readout.scale=Vector2(2,2)
        navigator.add_child(map_readout)
        bind_screen(nav_surface,navigator,false)
        rear_view=SubViewport.new()
        rear_view.size=Vector2i(416,110)
        rear_view.world_3d=get_world_3d()
        add_child(rear_view)
        rear_camera=Camera3D.new()
        rear_camera.cull_mask=1
        rear_camera.fov=23
        rear_camera.far=190
        var env:Environment=race.get_node("Atmosphere").environment.duplicate()
        env.ssr_enabled=false
        env.ssao_enabled=false
        env.glow_enabled=false
        rear_camera.environment=env
        rear_view.add_child(rear_camera)
        rear_camera.current=true
        bind_screen(mirror_surface,rear_view,true)
        cabin_light=OmniLight3D.new()
        cabin_light.light_cull_mask=8
        cabin_light.light_color=Color("#c8dadc")
        cabin_light.light_energy=.62
        cabin_light.light_specular=.12
        cabin_light.omni_range=1.65
        cabin_light.position=EYE+Vector3(.12,.12,-.08)
        add_child(cabin_light)
    set_active(false)

func bind_screen(mesh:MeshInstance3D,view:SubViewport,reverse:bool):
    var mat:=StandardMaterial3D.new()
    mat.shading_mode=BaseMaterial3D.SHADING_MODE_UNSHADED
    mat.albedo_texture=view.get_texture()
    if reverse:
        mat.uv1_scale.x=-1
        mat.uv1_offset.x=1
    mesh.material_override=mat

func set_active(active:bool):
    race.camera.set_cull_mask_value(3,not active)
    race.camera.set_cull_mask_value(4,active)
    race.camera.near=.025 if active else .05
    if cluster:
        var mode:=SubViewport.UPDATE_ALWAYS if active else SubViewport.UPDATE_DISABLED
        cluster.render_target_update_mode=mode
        navigator.render_target_update_mode=mode
        rear_view.render_target_update_mode=mode
        cabin_light.visible=active

func drive_camera(dt:float,snap:bool):
    var velocity:float=race.speed
    var steering:float=race.steer
    var cornering:=steering*clampf(absf(velocity)/23.,0.,1.)
    if snap:
        fore_aft=0.
        lateral=0.
    else:
        var accel:=clampf((velocity-last_speed)/maxf(dt,.001)/19.,-1.,1.)
        fore_aft=lerpf(fore_aft,accel,1.-exp(-dt*5.5))
        lateral=lerpf(lateral,cornering,1.-exp(-dt*6.5))
    last_speed=velocity
    var eye:=EYE+Vector3(-lateral*.021,-absf(lateral)*.006,fore_aft*.024)
    var aim:=Basis.from_euler(Vector3(deg_to_rad(-5.5)+fore_aft*.013,-lateral*.042,lateral*.014))
    race.camera.global_transform=race.body.global_transform*Transform3D(aim,eye)
    race.camera.fov=lerpf(64.,68.,absf(velocity)/53.)
    wheel.basis=Basis(STEERING_AXIS.normalized(),-steering*deg_to_rad(106.))
    for i in sleeves.size():
        var rest:=rest_sleeves[i]
        var wrist:=wheel.position+wheel.basis*(rest.origin-wheel.position)
        var original:=-rest.basis.z*.39
        var reach:=rest.origin+original-wrist
        var align:=Basis(Quaternion(original.normalized(),reach.normalized()))
        sleeves[i].transform=Transform3D(align*rest.basis.scaled_local(Vector3(1,1,reach.length()/original.length())),wrist)
    if rear_camera:
        rear_camera.global_transform=race.body.global_transform*Transform3D(Basis(Vector3.UP,PI),Vector3(0,1.12,2.48))
        readout.queue_redraw()
        map_readout.queue_redraw()

func _exit_tree():
    if is_instance_valid(cluster_surface):cluster_surface.material_override=null
    if is_instance_valid(mirror_surface):mirror_surface.material_override=null
    if is_instance_valid(nav_surface):nav_surface.material_override=null
