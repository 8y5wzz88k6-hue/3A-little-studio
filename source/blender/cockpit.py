"""Kestrel LHD interior. Blender coordinates are metres, with the nose along +Y."""
import math
import bpy


def build_cockpit(material, box, loft, tube, mesh, lettering, carbon, nickel, copper):
    leather = material('Cabin | midnight nappa', (.035, .043, .049), .04, .58)
    suede = material('Cabin | charcoal suede', (.025, .031, .035), .02, .79)
    enamel = material('Cabin | petrol enamel', (.042, .115, .132), .55, .30)
    pitch = material('Cabin | switch recess', (.008, .012, .016), .16, .40)
    nylon = material('Driver | woven flight suit',(.026,.055,.065),.035,.82)
    glove = material('Driver | graphite goatskin',(.049,.060,.065),.025,.68)
    guard = material('Driver | molded knuckle pads',(.019,.026,.030),.13,.48)
    thread = material('Cabin | saddle thread', (.39, .172, .080), 0, .76)
    ice = material('Cabin | luminous markings', (.38, .81, .75), .08, .44, .60)
    screen = material('Cabin | display glass', (.01, .018, .022), .12, .33)
    before = set(bpy.context.scene.objects)

    # Cross-car dash with rolled brow, dropped ends and a recessed passenger fascia.
    ribs = []
    for i in range(33):
        x = -.86 + i * 1.72 / 32
        arch = .029 * (1 - (x / .86) ** 2)
        sweep = .13 * (abs(x) / .86) ** 2
        ribs.append([(x, y+sweep, z+arch) for y,z in
                     [(.24,.615),(.22,.728),(.31,.796),(.66,.804),(.91,.758),(.94,.61)]])
    loft('Upholstered instrument panel', ribs, leather, .019)
    tube('Dash welt', [(r[2][0],r[2][1]-.005,r[2][2]+.001) for r in ribs], .005, thread)
    tube('Lower dash satin reveal', [(r[1][0],r[1][1]-.006,r[1][2]-.021) for r in ribs], .005, nickel)
    for side in (-1, 1):
        pillar = [(side*.81,.91,.757),(side*.78,.68,.866),(side*.731,.40,1.019),
                  (side*.675,.095,1.194),(side*.605,-.17,1.301)]
        sections=[]
        for j,(x,y,z) in enumerate(pillar):
            width=.030+.012*abs(j-2)/2
            sections.append([(x-width,y-.024,z),(x-width*.64,y-.043,z+.011),
                             (x+width,y-.023,z+.013),(x+width,y+.024,z),(x-width,y+.024,z)])
        loft('A-pillar trimmed in suede',sections,suede,.009)
        tube('Windscreen gasket',[(x-side*.04,y+.013,z) for x,y,z in pillar],.009,pitch)
        tube('Door upper sill',[(side*.81,-.66,.732),(side*.813,-.16,.748),
                               (side*.802,.38,.768),(side*.78,.73,.769)],.048,leather)
        loft('Sculpted door lining', [[(side*x,y,z) for x,z in
            [(w,.34),(w-.046,.54),(w-.066,.584),(w-.012,.724),(w+.039,.718),(w+.054,.34)]]
            for y,w in [(-.98,.78),(-.61,.80),(-.05,.814),(.44,.801),(.78,.764)]],leather,.014)
    header=[]
    for j in range(17):
        x=-.70+j*.0875
        z=1.305+.032*(1-(x/.70)**2)
        header.append([(x,-.23,z-.027),(x,-.13,z-.019),(x,-.11,z+.013),(x,-.25,z+.03)])
    loft('Windscreen header',header,suede,.011)

    def inset_display(name,x,y,z,width,height,material):
        # Normal points toward the seat. uv=(0,0) in Blender is the lower left.
        w=width/2;h=height/2
        ob=mesh(name,[(x-w,y-h*.23,z-h),(x+w,y-h*.23,z-h),
                      (x+w,y+h*.23,z+h),(x-w,y+h*.23,z+h)],[(0,1,2,3)],material)
        uv=ob.data.uv_layers.new(name='Display coordinates')
        for i,xy in enumerate([(0,0),(1,0),(1,1),(0,1)]):uv.data[i].uv=xy
        return ob

    cx=-.315
    loft('Cluster mounting plinth', [[(cx+x,y,z) for x,z in
        [(-.217,.790),(.217,.790),(.190,.862),(-.19,.862)]] for y in (.35,.45)],suede,.009)
    box('Instrument binnacle',(cx,.381,.892),(.499,.108,.142),pitch,.019)
    box('Glare shield',(cx,.376,.965),(.506,.151,.014),suede,.006)
    dash=inset_display('InstrumentDisplay',cx,.306,.891,.465,.120,screen)
    nav_x=.136
    box('Navigation tray',(nav_x,.226,.755),(.252,.073,.145),pitch,.012)
    navigator=inset_display('RouteDisplay',nav_x,.173,.755,.231,.130,screen)
    for x in (.395,.641):
        box('Vent bezel',(x,.240,.750),(.220,.034,.066),nickel,.010)
        box('Vent cavity',(x,.219,.750),(.207,.012,.054),pitch,.005)
        for v in range(4):
            box('Air guide',(x,.211,.732+v*.012),(.199,.011,.0035),leather,.001)
        box('Vent tab',(x+.032,.202,.750),(.022,.013,.016),copper,.002)
    lettering('Instrument panel signature','K E S T R E L',(.420,.231,.684),(math.pi/2,0,0),.023,nickel)
    for j in range(4):
        x=.04+j*.061
        box('Rocker recess',(x,.218,.667),(.052,.040,.033),pitch,.004)
        box('Tactile switch',(x,.192,.665),(.038,.018,.020),enamel,.004)
        box('Switch witness',(x,.180,.672),(.013,.002,.0025),ice,.0008)
    # The mirror has a physical housing and a dedicated live image surface.
    tube('Mirror stalk',[(.04,-.126,1.335),(.055,-.029,1.273),(.091,.075,1.235)],.010,pitch)
    box('Mirror frame',(.132,.095,1.228),(.240,.035,.074),pitch,.011)
    mirror=inset_display('MirrorDisplay',.132,.069,1.228,.211,.055,screen)
    # Flat-bottom perforated leather wheel with a copper centre index and thumb switches.
    loft('Transmission tunnel', [[(-w,y,.30),(-w,y,h-.045),(-w*.78,y,h),(w*.78,y,h),
         (w,y,h-.045),(w,y,.30)] for y,w,h in [(-.76,.12,.492),(-.32,.137,.520),(.04,.146,.554),(.32,.16,.64)]],leather,.012)
    for s in (-1,1):
        box('Footwell liner',(s*.41,-.04,.34),(.51,1.18,.051),suede,.017)
    static_parts=set(bpy.context.scene.objects)-before-{dash,mirror,navigator}
    wheel_before=set(bpy.context.scene.objects)
    hub=(cx,.018,.746)
    def wheelpoint(x,z,depth=0):
        return (cx+x,hub[1]+z*.235+depth,hub[2]+z)
    def rim_point(a,depth=0):
        return wheelpoint(.174*math.sin(a),max(-.122,.159*math.cos(a)),depth)
    tube('Leather steering rim',[rim_point(j*math.tau/104) for j in range(105)],.0195,leather)
    tube('Twelve oclock copper band',[rim_point((j-3)*.017,-.001) for j in range(7)],.0208,copper)
    for side in (-1,1):
        for j in range(17):
            a=side*(.82+j*.075)
            tube('Grip stitching',[rim_point(a,-.0175),rim_point(a+side*.032,-.0175)],.0016,thread)
        poly=[(.040,-.005),(.141,.033),(.163,.022),(.152,-.012),(.060,-.038)]
        loft('Forged wheel spoke',[[wheelpoint(side*x,z,d) for x,z in poly] for d in [-.008,.012]],nickel,.004)
        poly=[(.077,.000),(.141,.024),(.143,-.007),(.080,-.027)]
        loft('Thumb switch carrier',[[wheelpoint(side*x,z,d) for x,z in poly] for d in [-.018,-.009]],pitch,.003)
        for j in range(2):
            x=side*(.095+j*.023); z=-.005+j*.007
            box('Wheel switch',wheelpoint(x,z,-.024),(.014,.009,.011),copper if j else ice,.002)
        tube('Lower spoke',[wheelpoint(side*.022,-.033),wheelpoint(side*.060,-.119)],.009,nickel)
    box('Wheel boss',hub,(.132,.056,.080),pitch,.023)
    lettering('Wheel emblem','R / 9',wheelpoint(0,0,-.031),(math.pi/2,0,0),.031,nickel)
    # Continuous leather backs, articulated fingertips and a separate soft cuff.
    wrists=[]
    for side in (-1,1):
        def hand(x,depth,z):
            return wheelpoint(side*x,z,depth)
        def ring(x,depth,z,rx,ry):
            return [hand(x+rx*math.cos(j*math.tau/20),depth+ry*math.sin(j*math.tau/20),z) for j in range(20)]
        palm=loft('Precurved driving glove',[
            ring(.205,-.084,-.048,.029,.023),ring(.200,-.068,-.029,.035,.028),
            ring(.188,-.044,.005,.040,.029),ring(.174,-.027,.035,.044,.030),
            ring(.164,-.016,.059,.040,.026),ring(.159,-.005,.073,.029,.018)],glove,.005)
        for f in palm.data.polygons:f.use_smooth=True
        for k in range(4):
            x=.135+k*.016
            z=.061-(k-1)**2*.002
            tube('Wrapped glove finger',[hand(x,-.018,z),hand(x-.003,.004,z+.010),hand(x-.004,.022,z+.003),
                                        hand(x-.009,.031,z-.014),hand(x-.014,.025,z-.025)],.0095,glove)
            tube('Raised knuckle protector',[hand(x,-.043,z-.021),hand(x-.006,-.035,z-.005)],.0075,guard)
        tube('Gripping thumb',[hand(.174,-.047,.016),hand(.153,-.048,.025),hand(.136,-.039,.037),
                                hand(.128,-.016,.036),hand(.131,-.003,.026)],.014,glove)
        for j in range(2):
            tube('Glove saddle seam',[hand(.206+j*.012,-.091,-.042),hand(.199+j*.012,-.074,-.012),
                                      hand(.182+j*.012,-.058,.018)],.0015,thread)
        cuff=loft('Wrist closure',[ring(.208,-.089,-.051,.034,.029),ring(.204,-.082,-.038,.037,.030)],nylon,.003)
        wrists.append(hand(.206,-.087,-.048))
    wheel_parts=set(bpy.context.scene.objects)-wheel_before
    groups=[('CabinTrim',(0,0,0),static_parts),('SteeringWheel',hub,wheel_parts)]
    poses={}
    for side,wrist in zip((-1,1),wrists):
        name='SleeveL' if side<0 else 'SleeveR'
        before_sleeve=set(bpy.context.scene.objects)
        rings=[]
        for t,rx,rz in [(0,.032,.027),(.05,.036,.031),(.08,.039,.033),(.11,.036,.031),
                         (.14,.046,.038),(.19,.044,.036),(.25,.049,.041),(.30,.047,.040),(.35,.054,.045),(.39,.054,.046)]:
            rings.append([(rx*math.cos(j*math.tau/24),t,rz*math.sin(j*math.tau/24)) for j in range(24)])
        sleeve=loft('Nomex sleeve',rings,nylon,.003)
        for f in sleeve.data.polygons:f.use_smooth=True
        tube('Sleeve outer seam',[(r[0][0],r[0][1],.003) for r in rings],.0017,thread)
        groups.append((name,(0,0,0),set(bpy.context.scene.objects)-before_sleeve))
        poses[name]=(wrist,(cx+side*.28,-.44,.589))
    return ([(name,center,sorted(ob.name for ob in parts)) for name,center,parts in groups],
            {dash.name,mirror.name,navigator.name},poses)
