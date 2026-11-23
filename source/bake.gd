extends SceneTree

func _initialize():
    var data = JSON.parse_string(FileAccess.get_file_as_string("res://source/intermediate/manifest.json"))
    var buf = FileAccess.open("res://source/intermediate/mesh.bin", FileAccess.READ)
    var materials = {}
    for key in data.mats:
        var cfg = data.mats[key]
        var color = Color.from_string(cfg[0], Color.WHITE)
        if key.begins_with("facade") or key == "road":
            var sh = ShaderMaterial.new()
            sh.shader = load("res://shaders/asphalt.gdshader" if key == "road" else "res://shaders/facade.gdshader")
            if key != "road":
                sh.set_shader_parameter("cladding",color)
                sh.set_shader_parameter("seed",float(len(key)*17 + key.unicode_at(len(key)-1)))
            materials[key] = sh
        elif key in ["basalt","concrete","steel","metal","dark","walk","oxide","yellow"]:
            var sh = ShaderMaterial.new()
            sh.shader = load("res://shaders/surfaces.gdshader")
            sh.set_shader_parameter("coating", color)
            sh.set_shader_parameter("metalness",cfg[1])
            sh.set_shader_parameter("finish",cfg[2])
            materials[key] = sh
        else:
            var mat = StandardMaterial3D.new()
            mat.resource_name = key
            mat.albedo_color = color
            mat.metallic = cfg[1]
            mat.roughness = cfg[2]
            if cfg.size() >= 4:
                mat.emission_enabled = true
                mat.emission = color
                mat.emission_energy_multiplier = cfg[3]
            if cfg.size() == 5:
                mat.albedo_texture = load(cfg[4])
                mat.emission = Color.BLACK
                mat.emission_texture = mat.albedo_texture
                mat.emission_operator = BaseMaterial3D.EMISSION_OP_ADD
                mat.cull_mode = BaseMaterial3D.CULL_DISABLED
            materials[key] = mat
    var district = Node3D.new()
    district.name = "HarborDistrict"
    for entry in data.nodes:
        var mesh = ArrayMesh.new()
        for section in entry[1]:
            var spans = section[1]
            var chunks = []
            for span in spans:
                buf.seek(int(span[0]))
                chunks.append(buf.get_buffer(int(span[1])))
            var arrays = []
            arrays.resize(Mesh.ARRAY_MAX)
            arrays[Mesh.ARRAY_VERTEX] = chunks[0].to_vector3_array()
            arrays[Mesh.ARRAY_NORMAL] = chunks[1].to_vector3_array()
            arrays[Mesh.ARRAY_TEX_UV] = chunks[2].to_vector2_array()
            arrays[Mesh.ARRAY_INDEX] = chunks[3].to_int32_array()
            mesh.add_surface_from_arrays(Mesh.PRIMITIVE_TRIANGLES,arrays)
            mesh.surface_set_material(mesh.get_surface_count()-1,materials[section[0]])
        var part = MeshInstance3D.new()
        part.name = entry[0]
        part.mesh = mesh
        if not entry[0].begins_with("Road_") and entry[0] != "City_foundation":
            part.layers = 3
        district.add_child(part)
        part.owner = district
    var scene = PackedScene.new()
    var result = scene.pack(district)
    if result == OK:
        result = ResourceSaver.save(scene,"res://scenes/harbor.scn",ResourceSaver.FLAG_COMPRESS)
    print("District bake: ",error_string(result))
    district.free()
    quit(result)
