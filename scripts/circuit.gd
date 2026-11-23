extends Node3D

@onready var car: Node3D = $Kestrel
@onready var body: Node3D = $Kestrel/Body
@onready var camera: Camera3D = $Chase
@onready var hud: Control = $Overlay/Instruments
var points := PackedVector3Array()
var distance_total := 0.0
var spacing := 1.0
var route_index := 0
var route_t := 0.0
var progress := 0.0
var longitudinal := 0.0
var next_gate := 1
var lap := 1
var lap_time := 0.0
var best_time := 0.0
var last_time := 0.0
var started := false
var hold := false
var in_cockpit := false
var help := false
var speed := 0.0
var steer := 0.0
var yaw := 0.0
var motion := Vector3.ZERO
var wheel_angle := 0.0
var rim_nodes: Array[Node3D] = []
var light_specs: Array
var active_lights: Array[OmniLight3D] = []
var light_anchor := Vector3.INF
var notification := ""
var notice_time := 0.0
var audio: AudioStreamGeneratorPlayback
var phase := 0.0
var rpm_hz := 40.0
var muted := false
var persist_records := true
const PALETTE := {"aqua": Color("#39e4ef"), "warm": Color("#ffa25a"), "rose": Color("#ff247b"), "lav": Color("#946fff")}

func _ready():
    var data = JSON.parse_string(FileAccess.get_file_as_string("res://assets/course.json"))
    distance_total = data.length
    for p in data.points:
        points.append(Vector3(p[0],p[1],p[2]))
    spacing = distance_total / points.size()
    light_specs = data.lights
    for i in 16:
        var light := OmniLight3D.new()
        add_child(light)
        active_lights.append(light)
    for n in body.find_children("Wheel_*","Node3D",true,false):
        rim_nodes.append(n)
    var cfg := ConfigFile.new()
    if persist_records and cfg.load("user://tideline.cfg") == OK:
        best_time = cfg.get_value("lap","best",0.0)
    $Kestrel/DriverSeat.prepare(self)
    reset_to_road()
    refresh_lights()
    if DisplayServer.get_name() != "headless":
        $StreetOptics.prepare(self)
    if DisplayServer.get_name() != "headless":
        var stream := AudioStreamGenerator.new()
        stream.mix_rate = 22050
        stream.buffer_length = .13
        $Motor.stream = stream
        $Motor.play()
        audio = $Motor.get_stream_playback()
    hud.race = self

func tangent(i: int) -> Vector3:
    return (points[(i+1)%points.size()]-points[posmod(i-1,points.size())]).normalized()

func reset_to_road():
    var f := tangent(route_index)
    car.position = points[route_index].lerp(points[(route_index+1)%points.size()],route_t) + Vector3.UP*.028
    yaw = atan2(-f.x,-f.z)
    speed = 0.0
    steer = 0.0
    motion = Vector3.ZERO
    car.rotation = Vector3(asin(f.y),yaw,0)
    body.rotation = Vector3.ZERO
    update_camera(1.0,true)

func _unhandled_key_input(e: InputEvent):
    if not e is InputEventKey or not e.pressed or e.echo:
        return
    match e.physical_keycode:
        KEY_C:
            in_cockpit = not in_cockpit
            $Kestrel/DriverSeat.set_active(in_cockpit)
            update_camera(1.0,true)
        KEY_R:
            if not hold: reset_to_road()
        KEY_ESCAPE, KEY_P:
            hold = not hold
        KEY_H, KEY_F1:
            help = not help
        KEY_M:
            muted = not muted
            $Motor.volume_db = -80 if muted else -23

func key(a: Key, b: Key) -> bool:
    return Input.is_physical_key_pressed(a) or Input.is_physical_key_pressed(b)

func _physics_process(dt):
    if hold or points.is_empty(): return
    var throttle := key(KEY_W,KEY_UP)
    var brake := key(KEY_S,KEY_DOWN)
    var handbrake := Input.is_physical_key_pressed(KEY_SPACE)
    advance_drive(dt,throttle,brake,float(key(KEY_D,KEY_RIGHT))-float(key(KEY_A,KEY_LEFT)),handbrake)

func advance_drive(dt: float, throttle: bool, brake: bool, turn: float, handbrake: bool):
    if throttle or brake: started = true
    if started: lap_time += dt
    notice_time = maxf(0,notice_time-dt)
    if throttle: speed = move_toward(speed,53.0,(11.4 if speed>=0 else 23.0)*dt*(1.0-.55*clampf(speed/53,0,1)))
    elif brake: speed = move_toward(speed,-8.0,(23.5 if speed>0 else 6.5)*dt)
    else: speed = move_toward(speed,0,(2.15+.0018*speed*speed)*dt)
    if handbrake: speed = move_toward(speed,0,13.0*dt)
    steer = move_toward(steer,turn,dt*(3.8 if turn!=0 else 5.5))
    var steering_rate := lerpf(1.58,.75,clampf(absf(speed)/53,0,1))
    yaw -= steer*steering_rate*clampf(absf(speed)/4.8,0,1)*signf(speed)*dt*(1.45 if handbrake else 1.0)
    var forward := Vector3(-sin(yaw),0,-cos(yaw))
    motion = motion.lerp(forward*speed,1-exp(-dt*(2.2 if handbrake else 7.5)))
    car.position += motion*dt
    var old_progress := progress
    project_to_road()
    var delta_s := wrapf(progress-old_progress,-distance_total*.5,distance_total*.5)
    longitudinal += delta_s
    handle_gates()
    var t := tangent(route_index)
    car.rotation = Vector3(asin(clampf(t.y*forward.dot(Vector3(t.x,0,t.z).normalized()),-.3,.3)),yaw,0)
    body.rotation.z = lerpf(body.rotation.z,steer*minf(absf(speed)*.0016,.055),1-exp(-dt*7))
    wheel_angle = fmod(wheel_angle-speed/.389*dt,TAU)
    for wheel in rim_nodes:
        wheel.rotation = Vector3(wheel_angle,-steer*.38 if wheel.name.begins_with("Wheel_F") else 0.0,0)
    $Kestrel/TailGlow.light_energy = 1.85 if brake or handbrake else .58
    if not light_anchor.is_finite() or car.position.distance_squared_to(light_anchor)>30:
        refresh_lights()
    update_camera(dt)

func project_to_road():
    var nearest := INF
    var chosen := route_index
    var along := 0.0
    var p := Vector2(car.position.x,car.position.z)
    for k in range(-8,9):
        var i := posmod(route_index+k,points.size())
        var a := Vector2(points[i].x,points[i].z)
        var v := points[(i+1)%points.size()]-points[i]
        var line := Vector2(v.x,v.z)
        var t := clampf((p-a).dot(line)/line.length_squared(),0,1)
        var d := p.distance_squared_to(a+line*t)
        if d < nearest:
            nearest=d; chosen=i; along=t
    route_index=chosen; route_t=along
    progress=fposmod((chosen+along)*spacing,distance_total)
    var center := points[chosen].lerp(points[(chosen+1)%points.size()],along)
    var f := tangent(chosen)
    var right := Vector3(-f.z,0,f.x).normalized()
    var offset := (car.position-center).dot(right)
    var forward := Vector3(-sin(yaw),0,-cos(yaw))
    var limit := 7.90 - (1.18*absf(Vector3(-forward.z,0,forward.x).dot(right))+2.48*absf(forward.dot(right)))
    if absf(offset)>limit:
        car.position -= right*(offset-signf(offset)*limit)
        var outward := motion.dot(right)*signf(offset)
        if outward>0:
            motion -= right*signf(offset)*outward
            speed = move_toward(speed,0,outward*.065)
    car.position.y = center.y+.03

func handle_gates():
    if longitudinal < distance_total*next_gate/3.0: return
    if next_gate < 3:
        next_gate += 1
        notification = "进入轨道高架" if next_gate==2 else "进入铸造厂弯道"
    else:
        last_time = lap_time
        lap_time = 0
        lap += 1
        next_gate = 1
        longitudinal -= distance_total
        if best_time == 0 or last_time<best_time:
            best_time = last_time
            if persist_records:
                var cfg := ConfigFile.new()
                cfg.set_value("lap","best",best_time)
                cfg.save("user://tideline.cfg")
        notification = "完成一圈   "+lap_string(last_time)
    notice_time = 3.0

func refresh_lights():
    light_anchor=car.position
    var ranked: Array = []
    for spec in light_specs:
        var p := Vector3(spec[0],spec[1],spec[2])
        ranked.append([p.distance_squared_to(car.position),spec,p])
    ranked.sort_custom(func(a,b): return a[0]<b[0])
    for i in active_lights.size():
        var l := active_lights[i]
        var spec: Array = ranked[i][1]
        l.position=ranked[i][2]
        l.light_color=PALETTE[spec[3]]
        l.light_energy=3.5 if spec[4] else 8.2
        l.light_size=.12 if spec[4] else .38
        l.light_specular=.33 if spec[4] else .49
        l.omni_range=15.5 if spec[4] else 23.0
        l.omni_attenuation=1.15

func update_camera(dt: float,snap:=false):
    if in_cockpit:
        $Kestrel/DriverSeat.drive_camera(dt,snap)
        return
    var f := -car.basis.z.normalized()
    var pos := car.position
    var desired := pos - f*(5.75+absf(speed)*.020)+Vector3.UP*2.35
    camera.position = desired if snap else camera.position.lerp(desired,1-exp(-dt*9))
    var target := pos + f*6.8 + Vector3.UP*1.18
    camera.look_at(target,Vector3.UP)
    camera.fov=lerpf(64,75,absf(speed)/53)

func _process(dt):
    if audio:
        var frames := audio.get_frames_available()
        var gear := mini(5,int(absf(speed)/9))
        var hz := 32.0+absf(speed)*2.7-gear*11
        rpm_hz = lerpf(rpm_hz,hz,1-exp(-dt*8))
        var buffer := PackedVector2Array()
        buffer.resize(frames)
        for i in frames:
            phase=fmod(phase+TAU*rpm_hz/22050.0,TAU)
            var sample := 0.0 if hold else (sin(phase)+.36*sin(phase*2)+.17*sin(phase*4)+.08*sin(phase*7))*.38
            buffer[i]=Vector2(sample,sample)
        if frames: audio.push_buffer(buffer)
    hud.queue_redraw()

func lap_string(t: float) -> String:
    return "%02d:%02d.%03d"%[int(t/60),int(t)%60,int(t*1000)%1000]

func _exit_tree():
    if audio:
        $Motor.stop()
        $Motor.stream=null
        audio=null
