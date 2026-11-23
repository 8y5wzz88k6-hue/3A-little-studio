extends SceneTree

func _initialize():
    call_deferred("inspect")

func inspect():
    var race=load("res://scenes/circuit.tscn").instantiate()
    race.persist_records=false
    root.add_child(race)
    race.set_physics_process(false)
    await process_frame
    var toggle:=InputEventKey.new()
    toggle.physical_keycode=KEY_C
    toggle.pressed=true
    if "--cockpit-film" in OS.get_cmdline_user_args():
        race._unhandled_key_input(toggle)
        await drive_film(race)
    elif "--cockpit-photo" in OS.get_cmdline_user_args():
        race._unhandled_key_input(toggle)
        race.route_index=roundi(race.points.size()*.041)
        race.progress=race.route_index*race.spacing
        race.longitudinal=race.progress
        race.reset_to_road()
        race.refresh_lights()
        race.started=true
        race.speed=16.
        for i in 35:
            race.advance_drive(1./60.,false,false,0.,false)
            await RenderingServer.frame_post_draw
        var result=root.get_texture().get_image().save_png("res://preview/cockpit.png")
        print("Driver view captured: ",error_string(result))
    elif "--drive-film" in OS.get_cmdline_user_args():
        await drive_film(race)
    elif "--photos" in OS.get_cmdline_user_args():
        for shot in [["market",0.0],["viaduct",.379],["foundry",.733],["kestrel",.103]]:
            race.route_index=int(shot[1]*race.points.size())
            race.route_t=0
            race.progress=shot[1]*race.distance_total
            race.reset_to_road()
            race.refresh_lights()
            if shot[0]=="kestrel":
                race.hud.hide()
                race.camera.position=race.car.to_global(Vector3(-4.65,1.47,-5.5))
                race.camera.look_at(race.car.position+Vector3.UP*.71)
                race.camera.fov=47
            for i in 72: await RenderingServer.frame_post_draw
            var img=root.get_texture().get_image()
            img.save_png("res://preview/"+shot[0]+".png")
            print("Captured ",shot[0])
    else:
        race._unhandled_key_input(toggle)
        var seat=race.get_node("Kestrel/DriverSeat")
        if not race.in_cockpit or not race.camera.position.is_equal_approx(race.body.to_global(seat.EYE)):
            push_error("Driver eye anchor mismatch")
            quit(1)
            return
        race.advance_drive(1./60.,false,false,1.,false)
        if seat.wheel.basis.is_equal_approx(Basis.IDENTITY):
            push_error("Steering wheel did not turn")
            quit(1)
            return
        race.reset_to_road()
        var max_error=0.0
        var contact=0
        for step in 10000:
            var j=int((race.route_index+9)%race.points.size())
            var target=(race.points[j]-race.car.position).normalized()
            var angle=wrapf(atan2(-target.x,-target.z)-race.yaw,-PI,PI)
            var steering=clampf(-angle*3.9,-1,1)
            race.advance_drive(1.0/60.0,race.speed<15.0,false,steering,false)
            var err=race.car.position.distance_to(race.points[race.route_index])
            max_error=maxf(max_error,err)
            if err>5.5:contact+=1
            if race.lap>=2: break
        print("Drive check: lap=",race.lap," ordered checkpoint=",race.next_gate," time=",race.last_time," maximum centerline distance=",max_error," edge frames=",contact," rotating wheels=",race.rim_nodes.size())
        if race.lap!=2 or race.rim_nodes.size()!=4 or race.last_time<=0:
            quit(1)
            return
        race._unhandled_key_input(toggle)
        if race.in_cockpit or race.camera.get_cull_mask_value(4) or not race.camera.get_cull_mask_value(3):
            push_error("Chase camera visibility mismatch")
            quit(1)
            return
    race.queue_free()
    for i in 4: await process_frame
    quit()

func drive_film(race):
    # Record this with Godot Movie Maker at 30 fixed frames per second.
    for shot in [[0.,151],[.357,101],[.712,112]]:
        race.route_index=int(shot[0]*race.points.size())
        race.route_t=0.
        race.progress=race.route_index*race.spacing
        race.longitudinal=race.progress
        race.next_gate=1+int(shot[0]*3)
        race.reset_to_road()
        race.refresh_lights()
        race.speed=10.0
        race.started=true
        for i in shot[1]:
            for substep in 2:
                var j=int((race.route_index+9)%race.points.size())
                var target=(race.points[j]-race.car.position).normalized()
                var angle=wrapf(atan2(-target.x,-target.z)-race.yaw,-PI,PI)
                race.advance_drive(1.0/60.,race.speed<18,false,clampf(-angle*3.9,-1,1),false)
            await process_frame
