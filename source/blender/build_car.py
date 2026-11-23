"""Build the Kestrel R9 in Blender. +Y is the nose, measurements in metres."""
import bpy
from math import sin, cos, pi, exp, sqrt
from mathutils import Vector
from pathlib import Path

root=Path(__file__).resolve().parents[2]
bpy.ops.wm.read_factory_settings(use_empty=True)
def material(name,c,metal=0,rough=.38,emit=0):
    m=bpy.data.materials.new(name); m.diffuse_color=(*c,1); m.use_nodes=True
    p=next(n for n in m.node_tree.nodes if n.type=='BSDF_PRINCIPLED')
    for key,val in [('Base Color',(*c,1)),('Metallic',metal),('Roughness',rough),('Emission Color',(*c,1)),('Emission Strength',emit)]:
        p.inputs[key].default_value=val
    return m
pearl=material('Abyss petrol tri-coat',(.076,.265,.31),.68,.235)
orange=material('Anodized copper',(.74,.21,.067),.78,.27)
dark=material('Forged graphite',(.027,.038,.046),.72,.30)
rubber=material('Tread compound',(.017,.021,.025),0,.57)
rim=material('Machined nickel',(.47,.51,.49),.87,.22)
glass=material('Polarized canopy',(.013,.040,.056),.51,.09)
carbon=material('Carbon twill',(.019,.024,.032),.36,.32)
gasket=material('Recessed lamp ceramic',(.009,.013,.019),.49,.20)
red=material('Laser brake lamps',(1,.009,.038),.1,.21,4.5)
ice=material('Headlamp phosphor',(.70,.97,1),0,.15,6)
amber=material('Indicator',(1,.35,.05),.1,.3,3)
for m,coat in [(pearl,.94),(glass,.75),(carbon,.38),(orange,.44)]:
    p=next(n for n in m.node_tree.nodes if n.type=='BSDF_PRINCIPLED')
    p.inputs['Coat Weight'].default_value=coat
    p.inputs['Coat Roughness'].default_value=.09 if m==pearl else .15
def mesh(name,vs,faces,mat,bev=0,smooth=False):
    data=bpy.data.meshes.new(name); data.from_pydata(vs,[],faces); data.materials.append(mat); data.update()
    ob=bpy.data.objects.new(name,data); bpy.context.collection.objects.link(ob)
    if smooth:
        for p in data.polygons: p.use_smooth=True
    if bev:
        mod=ob.modifiers.new('Machined radii','BEVEL'); mod.width=bev; mod.segments=3
        norm=ob.modifiers.new('Corner normals','WEIGHTED_NORMAL')
    return ob
def loft(name,sections,mat,bev=.025):
    n=len(sections[0]); vs=sum(sections,[]); faces=[tuple(range(n)),tuple(reversed(range(len(vs)-n,len(vs))))]
    for j in range(len(sections)-1):
        for i in range(n):
            a=j*n+i; b=j*n+(i+1)%n; faces.append((a,a+n,b+n,b))
    # normals made consistent from enclosed volume (cross-section definitions vary)
    ob=mesh(name,vs,faces,mat,bev)
    import bmesh
    bm=bmesh.new(); bm.from_mesh(ob.data); bmesh.ops.recalc_face_normals(bm,faces=bm.faces); bm.to_mesh(ob.data); bm.free()
    return ob
def box(name,loc,sz,mat,bev=.015):
    x,y,z=loc; a,b,c=[v/2 for v in sz]
    return loft(name,[[(x-a,Y,z-c),(x+a,Y,z-c),(x+a,Y,z+c),(x-a,Y,z+c)] for Y in (y-b,y+b)],mat,bev)
def tube(name,coords,r,mat):
    c=bpy.data.curves.new(name,'CURVE'); c.dimensions='3D'; c.resolution_u=1; c.bevel_depth=r; c.bevel_resolution=2
    s=c.splines.new('POLY'); s.points.add(len(coords)-1)
    for p,co in zip(s.points,coords): p.co=(*co,1)
    ob=bpy.data.objects.new(name,c); bpy.context.collection.objects.link(ob); c.materials.append(mat); return ob
def cylinder(name,loc,r,depth,mat,bevel=.01):
    bpy.ops.mesh.primitive_cylinder_add(vertices=48,radius=r,depth=depth,rotation=(0,pi/2,0),location=loc)
    ob=bpy.context.object; ob.name=name; ob.data.materials.append(mat)
    for p in ob.data.polygons: p.use_smooth=len(p.vertices)==4
    if bevel:
        m=ob.modifiers.new('Rolled lip','BEVEL'); m.width=bevel; m.segments=3
    return ob

stations=[(-2.40,.93,.59),(-2.20,1.08,.75),(-1.53,1.15,.85),(-.93,1.08,.77),(-.28,1.02,.69),(.48,1.035,.69),(1.27,1.12,.765),(1.65,1.12,.727),(2.0,1.04,.615),(2.31,.91,.50),(2.47,.72,.424)]
def section(y):
    j=next((i for i in range(len(stations)-1) if y<=stations[i+1][0]),len(stations)-2)
    a,b,c,d=[stations[min(len(stations)-1,max(0,j+k))] for k in (-1,0,1,2)]
    t=min(1,max(0,(y-b[0])/(c[0]-b[0])))
    return tuple(.5*(2*B+(-A+C)*t+(2*A-5*B+4*C-D)*t*t+(-A+3*B-3*C+D)*t**3) for A,B,C,D in zip(a[1:],b[1:],c[1:],d[1:]))
def skin(y,u):
    w,h=section(y); u=abs(u)
    arch=max(exp(-((y-a)/.62)**2) for a in (-1.48,1.44))
    return h+.024*(1-u*u)+(.035+.10*arch)*exp(-((u-.82)/.20)**2)-.090*u**7
rings=[]
for j in range(109):
    y=-2.40+j*4.87/108; w,h=section(y)
    edge=max(.275,max(.387+sqrt(max(0,.421**2-(y-a)**2)) if abs(y-a)<.421 else .275 for a in (-1.48,1.44)))
    shoulder=max(skin(y,1),edge+.052)
    top=[(w*u/16,y,skin(y,u/16)) for u in range(-15,16)]
    rings.append([(-w*.94,y,edge),(-w,y,(shoulder+edge)*.5),(-w*.99,y,shoulder)]+top+[(w*.99,y,shoulder),(w,y,(shoulder+edge)*.5),(w*.94,y,edge),(w*.70,y,.265),(-w*.70,y,.265)])
body_shell=loft('01  /  hydroformed monocoque',rings,pearl,0)
import bmesh
cockpit_cut=bmesh.new()
cockpit_cut.from_mesh(body_shell.data)
upper_skin=[face for face in cockpit_cut.faces if all(abs(v.co.x)<.86 and
            -1.12<v.co.y<.94 and v.co.z>.55 for v in face.verts)]
bmesh.ops.delete(cockpit_cut,geom=upper_skin,context='FACES')
cockpit_cut.to_mesh(body_shell.data)
cockpit_cut.free()
for face in body_shell.data.polygons: face.use_smooth=len(face.vertices)==4
loft('Carbon perimeter splitter',[[(-w,y,.19),(-w,y,.242),(w,y,.242),(w,y,.19)] for y,w in [(-2.45,.99),(-2.17,1.10),(1.63,1.10),(2.43,.96),(2.5,.65)]],carbon)
canopy=[(-1.45,.65,.78,.82),(-.92,.82,.77,1.12),(-.55,.82,.73,1.27),(.12,.81,.72,1.30),(.54,.77,.70,1.14),(1.13,.65,.71,.77)]
canopy_shell=loft('02  /  curved panoramic canopy',[[(-w,y,b)]+[(w*u/10,y,b+(t-b)*max(0,1-(abs(u)/10)**3)**.58) for u in range(-9,10)]+[(w,y,b)] for y,w,b,t in canopy],glass,.018)
for face in canopy_shell.data.polygons:face.use_smooth=len(face.vertices)==4
loft('Floating roof',[[(-w,y,z-.025),(-w*.96,y,z),(w*.96,y,z),(w,y,z-.025)] for y,w,z in [(-.84,.55,1.17),(-.52,.58,1.296),(.11,.55,1.326),(.32,.49,1.266)]],dark,.02)
wheel_groups=[]
for s in (-1,1):
    loft('Flying rear buttress', [[(s*(x+dx),y,z+dz) for dx,dz in [(-.049,-.065),(.037,-.062),(.064,.004),(.021,.035),(-.027,.043)]] for y,x,z in [(-1.97,.80,.815),(-1.64,.78,.925),(-1.30,.72,.985),(-.99,.685,1.094),(-.70,.65,1.193),(-.54,.62,1.224)]],pearl,.016)
    tube('Buttress metal reveal',[(s*x,y,z) for y,x,z in [(-1.92,.82,.848),(-1.63,.80,.958),(-1.30,.74,1.018),(-.99,.705,1.127),(-.70,.67,1.226)]],.0065,rim)
    tube('Canopy reveal',[(s*w,y,b+.022) for y,w,b,t in canopy],.021,rim)
    tube('Windshield rail',[(s*w*.86,y,t-.060) for y,w,b,t in canopy],.027,pearl)
    for axle in (-1.48,1.44):
        before=set(bpy.context.scene.objects)
        cx=s*1.02; z=.389
        cylinder('Sport radial',(cx,axle,z),.386,.284,rubber,.034)
        xf=s*1.169
        cylinder('Recessed rim',(xf,axle,z),.298,.026,dark)
        cylinder('Brake rotor',(s*1.188,axle,z),.205,.015,rim,.003)
        for j in range(7):
            a=j*2*pi/7
            for fork in (-1,1):
                tubes=[(s*x,axle+r*cos(a+o),z+r*sin(a+o)) for x,r,o in [(1.236,.058,0),(1.212,.161,.045),(1.226,.269,fork*.132+.085)]]
                tube('Forged split spoke',tubes,.014,rim)
        for j in range(28):
            a=j*2*pi/28
            cylinder('Rotor perforation',(s*1.2,axle+.18*cos(a),z+.18*sin(a)),.008,.003,gasket,0)
        for j in range(5):
            a=j*2*pi/5
            cylinder('Titanium drive pin',(s*1.236,axle+.071*cos(a),z+.071*sin(a)),.012,.012,rim,.002)
        ring=[(s*1.206,axle+.287*cos(j*pi/36),z+.287*sin(j*pi/36)) for j in range(73)]
        tube('Rim bead',ring,.012,rim)
        cylinder('Center lock',(s*1.227,axle,z),.064,.026,orange,.005)
        wheel_groups.append(('Wheel_'+('F' if axle>0 else 'R')+('R' if s>0 else 'L'),(cx,axle,z),[ob.name for ob in set(bpy.context.scene.objects)-before]))
        box('Fixed ceramic brake caliper',(s*1.197,axle-.165,z+.03),(.028,.089,.219),orange,.018)
        sections=[]
        for j in range(33):
            ang=(-.19+j/32*(pi+.38))
            sections.append([(s*x,axle+r*cos(ang),z+r*sin(ang)) for x,r in [(1.07,.409),(1.202,.414),(1.182,.466),(1.02,.491)]])
        loft('Sculpted wheel brow',sections,pearl,.009)
    loft('Side intake blade', [[(s*x,y,z) for x,z in sect] for y,sect in [
        (-1.04,[(1.02,.31),(1.12,.34),(1.13,.69),(1.02,.72)]),
        (-.57,[(1.00,.28),(1.10,.31),(1.09,.56),(1.01,.61)]),
        (.83,[(1.00,.27),(1.09,.31),(1.04,.42),(.99,.47)])]],dark)
    tube('Rocker vermilion inlay',[(s*1.105,-1.04,.32),(s*1.116,-.61,.29),(s*1.087,.84,.31)],.026,orange)
    loft('Inset enamel door plaque',[[(s*(x+off),y,z) for off,z in [(0,.492),(.009,.514),(.007,top),(0,top+.01)]] for y,x,top in [(-.55,1.066,.573),(-.37,1.065,.624),(.29,1.054,.631),(.52,1.052,.585)]],carbon,.004)
    tube('Door shutline',[(s*.837,-.77,.745),(s*1.038,-.62,.62),(s*1.06,-.42,.44),(s*1.048,.67,.46),(s*.99,.83,.62)],.008,dark)
    tube('Mirror stem',[(s*.82,.44,.88),(s*.995,.34,.91)],.025,dark)
    box('Camera mirror',(s*1.035,.31,.92),(.16,.22,.085),pearl,.035)
    optic=[(.44,2.35),(.67,2.30),(.84,2.18),(.90,2.02),(.92,1.91)]
    tube('Split headlight housing',[(s*u*section(y)[0],y,skin(y,u)+.008) for u,y in optic],.043,gasket)
    tube('Split laser headlight',[(s*u*section(y)[0],y+.006,skin(y,u)+.044) for u,y in optic],.010,ice)
    for j in range(4):
        u=.60+j*.054; y=2.27-j*.035
        tube('Projector micro optics',[(s*section(y)[0]*u,y,skin(y,u)+.012),(s*section(y)[0]*(u+.022),y-.035,skin(y,u)+.026)],.011,ice)
    tube('Smoked rear lamp carrier',[(s*.06,-2.415,.556),(s*.80,-2.416,.564),(s*.97,-2.275,.638)],.047,gasket)
    tube('Laser tail signature',[(s*.06,-2.458,.566),(s*.80,-2.458,.574),(s*.985,-2.286,.655)],.012,red)
    for j in range(14):
        x=.20+j*.043
        tube('Tail optic fins',[(s*x,-2.456,.545),(s*(x+.014),-2.454,.558)],.005,red)
    for j in range(3):
        y=1.23+j*.115; w,h=section(y)
        tube('Fender extraction slots',[(s*w*u,y,skin(y,u)+.008) for u in (.68,.76,.85,.93)],.017,gasket)
    # Double curvature pearl surfaces wrap around a contrasting side intake.
    for j in range(4):
        tube('Intake vanes',[(s*1.106,-.92+j*.085,.395),(s*1.093,-.76+j*.085,.568-j*.012)],.014,rim)
    for j in range(3):
        y=-1.91+j*.18
        box('Buttress mounting stud',(s*.83,y,skin(y,.76)+.012),(.025,.03,.012),rim,.003)
    for j in range(5):
        box('Fender outlet',(s*.855,-1.41+j*.095,.849-j*.006),(.195,.032,.021),dark,.006)
    box('Wing pedestal',(s*.62,-2.07,.828),(.085,.22,.21),dark)
    tube('Hood crease',[(s*.32,2.32,.484),(s*.44,1.84,.70),(s*.48,1.17,.794)],.012,dark)
loft('03  /  swept carbon aerofoil',[[(x,y-.17,z+.035),(x,y+.16,z-.015),(x,y+.10,z-.042),(x,y-.17,z+.004)] for x,y,z in [(-1.16,-2.12,.98),(-1.04,-2.11,.97),(-.62,-2.04,.92),(0,-2.01,.913),(.62,-2.04,.92),(1.04,-2.11,.97),(1.16,-2.12,.98)]],carbon,.011)
for s in (-1,1):
    loft('Copper aerofoil end fence',[[(s*x,y,z) for y,z in [(-2.36,.972),(-2.30,1.045),(-1.97,.992),(-1.96,.902),(-2.26,.912)]] for x in (1.148,1.167)],orange,.008)
    for j in range(2):
        x=s*(.62+j*.12)
        tube('Exhaust rolled lip',[(x+.055*cos(n*pi/20),-2.448,.315+.041*sin(n*pi/20)) for n in range(41)],.011,rim)
        box('Exhaust throat',(x,-2.43,.314),(.113,.023,.087),gasket,.018)
    for off in (.44,.47):
        tube('Coachline',[(s*section(y)[0]*off,y,skin(y,off)+.006) for y in [1.09+j*.055 for j in range(22)]],.0045,orange)
    for y in (-1.80,-1.71,-1.62):
        tube('Ribbed rear shoulders',[(s*section(y)[0]*u,y,skin(y,u)+.015) for u in (.66,.72,.82,.89)],.014,gasket)
box('Rear grille',(0,-2.386,.447),(1.79,.055,.179),dark)
for i in range(-18,19):
    for row in (-1,0,1):
        x=i*.047+(row%2)*.024; z=.439+row*.038
        tube('Rear grille honeycomb',[(x+.025*cos(j*pi/3),-2.422,z+.022*sin(j*pi/3)) for j in range(7)],.0038,rim)
for i in range(-4,5):
    box('Diffuser vane',(i*.178,-2.28,.226),(.025,.37,.135),dark,.008)
for i in range(8):
    y=-1.39-i*.092
    box('Engine cover louver',(0,y,skin(y,0)+.021),(.97+i*.014,.055,.038),carbon,.010)
box('Front intake mouth',(0,2.462,.335),(1.31,.076,.133),gasket,.038)
for i in range(-11,12):
    box('Front intake strakes',(i*.054,2.506,.327),(.012,.026,.065),dark,.004)
box('Rear homologation plate',(0,-2.432,.455),(.63,.017,.127),dark)
def lettering(name,content,loc,rot,size,mat):
    c=bpy.data.curves.new(name,'FONT'); c.body=content; c.align_x='CENTER'; c.align_y='CENTER'; c.size=size; c.space_character=1.1
    ob=bpy.data.objects.new(name,c); bpy.context.collection.objects.link(ob); ob.location=loc; ob.rotation_euler=rot; c.materials.append(mat)
lettering('Registration','KS  •  09',(0,-2.444,.458),(pi/2,0,0),.093,ice)
lettering('Hood emblem','R 9',(0,1.7,skin(1.7,0)+.012),(-.18,0,pi),.13,rim)
for s in (-1,1):
    lettering('Door team insignia','09   /   KESTREL',(s*1.084,-.015,.565),(pi/2,0,s*pi/2),.089,rim)
for j in range(5):
    y=-1.32+j*.081
    _,w,b,t=next(row for row in canopy if row[0]>=y)
    t=.82+(y+1.45)*(.30/.53);w=.65+(y+1.45)*(.17/.53)
    tube('Heated rear glazing',[(w*u,y,.785+(t-.785)*max(0,1-abs(u)**3)**.58+.007) for u in [-.81,-.62,-.39,0,.39,.62,.81]],.0037,orange)
import runpy
build_cockpit=runpy.run_path(str(Path(__file__).with_name('cockpit.py')))['build_cockpit']
cabin_groups,display_names,sleeve_poses=build_cockpit(material,box,loft,tube,mesh,lettering,carbon,rim,orange)
outer_glass=[canopy_shell.name,'Floating roof']+[ob.name for ob in bpy.context.scene.objects if ob.name.startswith(('Windshield rail','Canopy reveal'))]
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.convert(target='MESH')
def join_parts(name,parts,center):
    bpy.ops.object.select_all(action='DESELECT')
    for ob in parts: ob.select_set(True)
    bpy.context.view_layer.objects.active=parts[0]
    bpy.ops.object.join()
    ob=bpy.context.object; ob.name=name
    bpy.context.scene.cursor.location=center
    bpy.ops.object.origin_set(type='ORIGIN_CURSOR')
    bpy.ops.object.transform_apply(location=False,rotation=True,scale=True)
separate_groups=wheel_groups+cabin_groups+[('OuterCanopy',(0,0,0),outer_glass)]
for name,center,names in separate_groups:
    join_parts(name,[bpy.data.objects[n] for n in sorted(names)],center)
independent=display_names|{name for name,_,_ in separate_groups}
join_parts('Kestrel_body',[ob for ob in bpy.context.scene.objects if ob.name not in independent],(0,0,0))
for name,(wrist,elbow) in sleeve_poses.items():
    ob=bpy.data.objects[name]
    direction=Vector(elbow)-Vector(wrist)
    ob.location=wrist
    ob.rotation_mode='QUATERNION'
    ob.rotation_quaternion=direction.to_track_quat('Y','Z')
    ob.scale.y=direction.length/.39
import numpy as np
yy,xx=np.mgrid[0:256,0:256]
u=(xx+yy)/16; v=(xx-yy)/16
warp=((np.floor(u)+2*np.floor(v))%4)<2
strand=np.where(warp,np.sin(np.pi*(u%1)),np.sin(np.pi*(v%1)))
filament=np.where(warp,np.cos(5*np.pi*u),np.cos(5*np.pi*v))
value=.10+.12*strand+.018*filament
pixels=np.stack([value*.85,value*.94,value,np.ones_like(value)],axis=-1).astype(np.float32)
twill=bpy.data.images.new('2x2 diagonal twill',width=256,height=256)
twill.pixels.foreach_set(pixels.ravel());twill.pack()
tex=carbon.node_tree.nodes.new('ShaderNodeTexImage');tex.image=twill
carbon.node_tree.links.new(tex.outputs['Color'],next(n for n in carbon.node_tree.nodes if n.type=='BSDF_PRINCIPLED').inputs['Base Color'])
for ob in bpy.context.scene.objects:
    if ob.type!='MESH' or ob.name in display_names:continue
    layer=ob.data.uv_layers.active or ob.data.uv_layers.new(name='Fabric coordinates')
    for p in ob.data.polygons:
        axis=max(range(3),key=lambda i:abs(p.normal[i]))
        ax,ay=[i for i in range(3) if i!=axis]
        for j in p.loop_indices:
            co=ob.data.vertices[ob.data.loops[j].vertex_index].co
            layer.data[j].uv=(co[ax]*7.2,co[ay]*7.2)
bpy.context.preferences.filepaths.save_version=0
bpy.context.scene.world=bpy.data.worlds.new('Studio')
bpy.ops.wm.save_as_mainfile(filepath=str(root/'source/blender/Kestrel_R9.blend'))
bpy.ops.export_scene.gltf(filepath=str(root/'assets/Kestrel_R9.glb'),export_format='GLB',export_apply=True)
