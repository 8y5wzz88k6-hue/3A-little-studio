extends Node3D

var race
var reflection: SubViewport
var mirror: Camera3D
var asphalt: ShaderMaterial

func prepare(circuit):
    race=circuit
    var road= race.get_node("District/Road_00").mesh
    for i in road.get_surface_count():
        var mat=road.surface_get_material(i)
        if mat is ShaderMaterial and mat.shader==preload("res://shaders/asphalt.gdshader"):
            asphalt=mat
            break
    reflection=SubViewport.new()
    reflection.render_target_update_mode=SubViewport.UPDATE_ALWAYS
    reflection.world_3d=get_world_3d()
    add_child(reflection)
    mirror=Camera3D.new()
    mirror.cull_mask=2
    var env: Environment=race.get_node("Atmosphere").environment.duplicate()
    env.ssr_enabled=false
    env.ssao_enabled=false
    env.glow_enabled=false
    mirror.environment=env
    mirror.far=270
    reflection.add_child(mirror)
    mirror.current=true
    asphalt.set_shader_parameter("city_mirror",reflection.get_texture())
    asphalt.set_shader_parameter("mirror_on",1.0)
    var contact:=MeshInstance3D.new()
    var plane:=PlaneMesh.new()
    plane.size=Vector2(3.26,5.75)
    var shadow:=ShaderMaterial.new()
    shadow.shader=preload("res://shaders/contact.gdshader")
    plane.material=shadow
    contact.mesh=plane
    contact.cast_shadow=GeometryInstance3D.SHADOW_CASTING_SETTING_OFF
    race.car.add_child(contact)
    contact.position.y=.005
    for i in 19:
        var idx:int=roundi((i+.27)*race.points.size()/19.0)
        var tangent:Vector3=race.tangent(idx)
        var side:=Vector3(-tangent.z,0,tangent.x).normalized()
        var puff:=MeshInstance3D.new()
        var mesh:=QuadMesh.new()
        mesh.size=Vector2(3.1,4.4) if i<13 else Vector2(4.4,5.7)
        var mat:=ShaderMaterial.new()
        mat.shader=preload("res://shaders/steam.gdshader")
        mat.set_shader_parameter("offset",i*3.4)
        mat.set_shader_parameter("tint",[Color("#b6b5d5"),Color("#82c8c8"),Color("#cb9b99")][i%3])
        mesh.material=mat
        puff.mesh=mesh
        puff.cast_shadow=GeometryInstance3D.SHADOW_CASTING_SETTING_OFF
        add_child(puff)
        puff.position=race.points[idx]+side*(8.8 if i%2 else -9.2)+Vector3.UP*(.18+mesh.size.y*.5)
    get_viewport().size_changed.connect(resize_reflection)
    resize_reflection()
    sync_mirror()

func resize_reflection():
    reflection.size=Vector2i(get_viewport().get_visible_rect().size*.55).max(Vector2i(2,2))

func _process(_dt):
    if mirror: sync_mirror()

func sync_mirror():
    var camera:Camera3D=race.camera
    var tangent:Vector3=race.tangent(race.route_index)
    var road_up:=Vector3(-tangent.z,0,tangent.x).cross(tangent).normalized()
    var pivot:Vector3=race.car.position-Vector3.UP*.03
    var delta:=camera.global_position-pivot
    var center:=camera.global_position-2.*road_up*delta.dot(road_up)
    var forward:=(-camera.global_basis.z).bounce(road_up)
    var up:= -camera.global_basis.y.bounce(road_up)
    mirror.global_transform=Transform3D(Basis.looking_at(forward,up),center)
    mirror.fov=camera.fov
    var matrix:=mirror.get_camera_projection()*Projection(mirror.global_transform.affine_inverse())
    asphalt.set_shader_parameter("mirror_view_projection",matrix)

func _exit_tree():
    if asphalt:
        asphalt.set_shader_parameter("mirror_on",0.)
        asphalt.set_shader_parameter("city_mirror",null)
    if reflection:
        reflection.render_target_update_mode=SubViewport.UPDATE_DISABLED
