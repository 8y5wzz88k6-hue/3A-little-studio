extends SceneTree

# Capture the market's incident light into an HDR lighting panorama. The game
# needs no live cubemap captures when it enters a new stretch of the circuit.
func _initialize():
    call_deferred("bake")

func bake():
    var data=JSON.parse_string(FileAccess.get_file_as_string("res://assets/course.json"))
    var city=load("res://scenes/circuit.tscn").instantiate()
    city.set_script(null)
    for path in ["Kestrel","Overlay","Chase","Motor","StreetOptics"]:city.get_node(path).free()
    root.add_child(city)
    var env:Environment=city.get_node("Atmosphere").environment.duplicate()
    env.sky=Sky.new()
    var dusk:=ProceduralSkyMaterial.new()
    dusk.sky_top_color=Color("#0a0a20")
    dusk.sky_horizon_color=Color("#342a49")
    env.sky.sky_material=dusk
    env.glow_enabled=false
    env.ssr_enabled=false
    env.ssao_enabled=false
    env.tonemap_mode=Environment.TONE_MAPPER_LINEAR
    var point=Vector3(0,2.0,72)
    var palette={"warm":Color("#ffa25a"),"aqua":Color("#39e4ef"),"rose":Color("#ff247b"),"lav":Color("#946fff")}
    for spec in data.lights:
        var pos=Vector3(spec[0],spec[1],spec[2])
        if pos.distance_to(point)>66:continue
        var lamp:=OmniLight3D.new()
        lamp.position=pos
        lamp.light_color=palette[spec[3]]
        lamp.light_energy=3.5 if spec[4] else 8.2
        lamp.omni_range=19
        city.add_child(lamp)
    var view:=SubViewport.new()
    view.world_3d=root.world_3d
    view.size=Vector2i(512,512)
    view.use_hdr_2d=true
    view.render_target_update_mode=SubViewport.UPDATE_ALWAYS
    root.add_child(view)
    var cam:=Camera3D.new()
    cam.position=point
    cam.environment=env
    cam.fov=90
    cam.cull_mask=2
    view.add_child(cam)
    cam.current=true
    var faces:Array[Image]=[]
    var orientations:Array[Basis]=[]
    for dir in [Vector3.RIGHT,Vector3.LEFT,Vector3.UP,Vector3.DOWN,Vector3.BACK,Vector3.FORWARD]:
        var up=Vector3.FORWARD if abs(dir.y)>.9 else Vector3.UP
        cam.look_at(point+dir,up)
        orientations.append(cam.global_basis.inverse())
        for frame in 4:await RenderingServer.frame_post_draw
        faces.append(view.get_texture().get_image())
    var pano=Image.create_empty(1024,512,false,Image.FORMAT_RGBH)
    var peak:=0.
    for y in 512:
        var theta=(y+.5)*PI/512.
        for x in 1024:
            var phi=((x+.5)/1024.-.5)*TAU
            var dir=Vector3(cos(phi)*sin(theta),cos(theta),sin(phi)*sin(theta))
            var axis=dir.abs().max_axis_index()
            var side=axis*2+(0 if dir[axis]>0 else 1)
            var v=orientations[side]*dir
            var u=clampi(int((v.x/-v.z*.5+.5)*512),0,511)
            var row=clampi(int((.5-v.y/-v.z*.5)*512),0,511)
            var color=faces[side].get_pixel(u,row)
            peak=maxf(peak,maxf(color.r,maxf(color.g,color.b)))
            pano.set_pixel(x,y,color)
    var err=pano.save_exr("res://assets/harbor_radiance.exr",false)
    print("HDR panorama: ",error_string(err),"   highest radiance: ",peak)
    quit(err)
