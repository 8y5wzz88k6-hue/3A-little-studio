"""Author the closed road, architecture and street furniture for the Godot baker."""
import math, json, random, struct
from array import array
from pathlib import Path
from collections import defaultdict

ROOT=Path(__file__).resolve().parents[1]
BUILD=ROOT/'source'/'intermediate'
BUILD.mkdir(exist_ok=True)
rng=random.Random(207)
def add(a,b): return tuple(x+y for x,y in zip(a,b))
def sub(a,b): return tuple(x-y for x,y in zip(a,b))
def mul(a,k): return tuple(x*k for x in a)
def dot(a,b): return sum(x*y for x,y in zip(a,b))
def unit(a): return mul(a,1/max(math.sqrt(dot(a,a)),1e-10))
def cross(a,b): return (a[1]*b[2]-a[2]*b[1],a[2]*b[0]-a[0]*b[2],a[0]*b[1]-a[1]*b[0])
def dist(a,b): return math.sqrt(dot(sub(a,b),sub(a,b)))

# A fast market straight, ascending S, viaduct sweeper and two tight return corners.
knots=[(0,102),(0,56),(0,-18),(12,-64),(51,-103),(78,-151),(128,-158),(160,-124),(151,-69),(179,-36),(213,-7),(209,46),(171,73),(133,66),(108,88),(94,143),(47,160),(11,143)]
raw=[]
for i in range(len(knots)):
    a,b,c,d=[knots[j%len(knots)] for j in (i-1,i,i+1,i+2)]
    for j in range(45):
        t=j/45
        raw.append(tuple(.5*(2*B+(-A+C)*t+(2*A-5*B+4*C-D)*t*t+(-A+3*B-3*C+D)*t**3) for A,B,C,D in zip(a,b,c,d)))
raw.append(raw[0])
lengths=[0]
for a,b in zip(raw,raw[1:]): lengths.append(lengths[-1]+dist(a,b))
L=lengths[-1]; N=round(L/1.7); ds=L/N
def altitude(s):
    t=s/L
    if .23<t<.64: return 8.5*math.sin(math.pi*(t-.23)/.41)**2
    return 0
points=[]; j=0
for i in range(N):
    s=i*ds
    while lengths[j+1]<s:j+=1
    p=add(raw[j],mul(sub(raw[j+1],raw[j]),(s-lengths[j])/(lengths[j+1]-lengths[j])))
    points.append((p[0],altitude(s),p[1]))
def frame(s):
    f=(s%L)/ds; i=int(f)%N
    c=add(points[i],mul(sub(points[(i+1)%N],points[i]),f-int(f)))
    v=sub(points[(i+1)%N],points[(i-1)%N]); v=unit((v[0],0,v[2]))
    return c,(-v[2],0,v[0]),v
def local(s,x,y,z=0):
    c,r,f=frame(s); return add(add(add(c,mul(r,x)),(0,y,0)),mul(f,z))

materials={
'concrete':('596673',.32,.64),'basalt':('343C4B',.44,.67),'steel':('536275',.74,.38),'metal':('89939B',.76,.37),
'oxide':('A34332',.55,.48),'yellow':('E2A845',.34,.48),'dark':('1C2734',.44,.49),'glass':('38576B',.76,.23),
'facade':('3C4E59',.42,.44),'facadeB':('56454C',.51,.43),'facadeC':('515A67',.56,.46),
'road':('29313C',.4,.28),'white':('A4ABB0',.13,.61),'paint':('E7AE54',.17,.59),'walk':('55606C',.18,.72),
'cyan':('26F4E1',.18,.23,3.6),'rose':('FF267F',.2,.27,4.2),'gold':('FF9E48',.25,.28,2.7),
'lamp':('E5FFF1',.11,.26,3.0),'red':('FF563B',.24,.29,2.7),'lav':('986BFF',.22,.3,3.2),
'tealglass':('477C84',.52,.29,.32),'warmglass':('AA8263',.38,.32,.32)}
for p in (ROOT/'assets/signs').glob('*.png'):
    energy=.12 if p.stem=='shutter' else (.66 if p.stem.startswith('room_') else 1.45)
    if p.stem in ['market','arc','coil','relay','transit']:energy=2.55
    materials[p.stem]=('FFFFFF',0,.55,energy,'res://assets/signs/'+p.name)
groups={}; G=None
def group(name):
    global G
    G=groups.setdefault(name,{})
def polygon(mat,verts,out=None,uv=None):
    b=G.get(mat)
    if b is None:
        b=(array('f'),array('f'),array('f'),array('i'));G[mat]=b
    pos,nor,tex,ix=b; k=len(pos)//3
    n=unit(cross(sub(verts[1],verts[0]),sub(verts[2],verts[0])))
    flip=out is not None and dot(n,out)<0
    if flip:n=mul(n,-1)
    if uv is None:
        a=dist(verts[0],verts[1]); h=dist(verts[0],verts[-1])
        uv=[(0,0),(a,0),(a,h),(0,h)]
    for v,t in zip(verts,uv):pos.extend(v);nor.extend(n);tex.extend(t)
    for j in range(1,len(verts)-1): ix.extend((k,k+j,k+j+1) if flip else (k,k+j+1,k+j))
def cube_at(mat,center,R,F,w,h,d):
    vs=[add(add(add(center,mul(R,x*w/2)),(0,y*h/2,0)),mul(F,z*d/2)) for x,y,z in [(-1,-1,-1),(1,-1,-1),(1,1,-1),(-1,1,-1),(-1,-1,1),(1,-1,1),(1,1,1),(-1,1,1)]]
    for face in [(3,2,1,0),(6,7,4,5),(7,3,0,4),(2,6,5,1),(7,6,2,3),(0,1,5,4)]:
        q=[vs[j] for j in face]; polygon(mat,q,sub(tuple(sum(v[k] for v in q)/4 for k in range(3)),center))
def box(s,x,y,z,w,h,d,m):
    c,r,f=frame(s);cube_at(m,local(s,x,y,z),r,f,w,h,d)
def beam(a,b,r,m,sides=7):
    v=unit(sub(b,a)); u=unit(cross(v,(0,1,0) if abs(v[1])<.9 else (1,0,0))); w=cross(v,u)
    ring=[mul(add(mul(u,math.cos(i*math.tau/sides)),mul(w,math.sin(i*math.tau/sides))),r) for i in range(sides)]
    for i,off in enumerate(ring):
        off2=ring[(i+1)%sides];polygon(m,[add(a,off),add(b,off),add(b,off2),add(a,off2)],add(off,off2))
def strut(s,a,b,r,m,sides=7):beam(local(s,*a),local(s,*b),r,m,sides)
def face_sign(s,x,y,z,w,h,mat,nx,nz):
    # The screen's right axis follows the observer's right when facing it.
    c,r,f=frame(s); n=unit(add(mul(r,nx),mul(f,nz))); right=unit(cross((0,1,0),n)); cent=local(s,x,y,z)
    def panel(width,height,offset,material,xx=0,yy=0):
        mid=add(add(add(cent,mul(n,offset)),mul(right,xx)),(0,yy,0))
        q=[add(add(mid,mul(right,a*width/2)),(0,b*height/2,0)) for a,b in [(-1,1),(1,1),(1,-1),(-1,-1)]]
        polygon(material,q,n,[(0,0),(1,0),(1,1),(0,1)])
    panel(w+.43,h+.43,0,'dark');panel(w,h,.04,mat)
    panel(.08,h*.9,.05,'gold',-w/2-.12)

# Road ribbons share endpoints, including grade changes and the start seam.
def ribbon(s1,s2,x1,x2,y,mat):
    q=[local(s1,x1,y),local(s1,x2,y),local(s2,x2,y),local(s2,x1,y)]
    polygon(mat,q,(0,1,0),[(x1,s1),(x2,s1),(x2,s2),(x1,s2)])
for i in range(N):
    s=i*ds; e=s+ds; group('Road_%02d'%(i//40))
    ribbon(s,e,-7.9,7.9,0,'road')
    for side in (-1,1):
        ribbon(s,e,side*7.9,side*11.5,.18,'walk')
        a,b,c,d=[local(d0,side*7.9,h) for d0,h in [(s,.18),(e,.18),(e,-.05),(s,-.05)]]
        polygon('metal',[a,b,c,d],mul(frame(s)[1],-side))
        ribbon(s,e,side*7.22,side*7.32,.016,'white')
        ribbon(s,e,side*.10,side*.18,.018,'paint')
        if i%5<2:ribbon(s,e,side*3.66,side*3.77,.019,'white')
        if altitude(s)>.2:
            q=[local(a,side*11.45,h) for a,h in [(s,.17),(e,.17),(e,-1.55),(s,-1.55)]]
            polygon('basalt',q,mul(frame(s)[1],side))
for i in range(24):
    for j in range(3):
        if (i+j)%2==0:ribbon(j*.61,(j+1)*.61,-7.2+i*.60,-6.60+i*.60,.025,'white')
lamps=[]
for k in range(round(L/12)):
    s=k*L/round(L/12)+3; group('Street_furniture_%02d'%(k//9))
    for side in (-1,1):
        box(s,side*8.28,.62,0,.43,.88,3.25,'concrete')
        box(s,side*8.28,1.073,0,.46,.06,3.3,'yellow' if (k//4)%2 else 'metal')
        box(s,side*8.045,.74,-.74,.05,.14,.54,'gold' if side==1 else 'cyan')
        for z in [-2.6,2.6]:
            box(s,side*8.48,.52,z,.17,.81,.17,'metal')
        box(s,side*8.48,.72,0,.12,.14,5.5,'steel')
        if k%2==(1 if side==1 else 0):
            strut(s,(side*9.5,.2,0),(side*9.5,6.3,0),.105,'steel')
            strut(s,(side*9.5,6.25,0),(side*7.3,6.98,0),.086,'metal')
            box(s,side*7.22,6.97,0,1.1,.18,.43,'dark');box(s,side*7.22,6.863,0,.9,.03,.32,'lamp')
            lamps.append([*local(s,side*6.9,6.55), 'aqua' if k%4<2 else 'warm',1])
    if k%4==0 and altitude(s)>2:
        box(s,0,-altitude(s)/2-.55,0,3.8,altitude(s)+1.1,2.8,'concrete')
    if k%7==3:
        for z in [-1.5,0,1.5]:
            box(s,-9.5,.28,z,.57,.17,.89,'steel')

shops=['market','arc','relay','coil','transit']
ads=['vesper','pelagic','soup','vector','phase','medusa','orbit','fold']
def loop_tube(s,path,r,mat):
    for a,b in zip(path,path[1:]):strut(s,a,b,r,mat,8)

def paper_lantern(s,x,y,z,scale):
    profile=[(-.48,.16),(-.43,.25),(-.29,.34),(0,.385),(.29,.34),(.43,.25),(.48,.16)]
    sides=16
    for (h1,r1),(h2,r2) in zip(profile,profile[1:]):
        for n in range(sides):
            a=n*math.tau/sides;b=(n+1)*math.tau/sides
            q=[local(s,x+scale*r*math.cos(t),y+scale*h,z+scale*r*math.sin(t)) for h,r,t in [(h1,r1,a),(h1,r1,b),(h2,r2,b),(h2,r2,a)]]
            polygon('gold' if n%5 else 'red',q,sub(q[0],local(s,x,y,z)))
    for h,r in profile[::2]:
        loop_tube(s,[(x+scale*r*math.cos(n*math.tau/sides),y+h*scale,z+scale*r*math.sin(n*math.tau/sides)) for n in range(sides+1)],.015,'oxide')
    box(s,x,y+.49*scale,z,.31*scale,.10,.31*scale,'dark')
    strut(s,(x,y+.53*scale,z),(x,y+1.1*scale,z),.019,'dark')

def street_stall(s,side,street,depth,k):
    x=side*(street-2.2); z=depth*.16
    box(s,x,1.00,z,1.17,1.66,3.55,'oxide' if k%2 else 'concrete')
    box(s,x,1.88,z,1.37,.14,3.75,'metal')
    for a in [-1.54,1.54]:
        strut(s,(x-side*.48,1.88,z+a),(x-side*.48,3.47,z+a),.044,'metal')
    for j in range(7):
        zz=z-1.75+j*.5
        q=[local(s,x+side*xx,hh,zz+dz) for xx,hh,dz in [(.83,3.76,0),(-.83,3.42,0),(-.83,3.42,.51),(.83,3.76,.51)]]
        polygon('oxide' if j%2 else 'yellow',q,(0,1,0))
        box(s,x-side*.83,3.32,zz+.25,.035,.21,.51,'oxide' if j%2 else 'yellow')
    for j in range(6):
        zz=z-1.34+j*.52
        strut(s,(x,1.95,zz),(x,2.09+(j%3)*.06,zz),.15,'metal',12)
        strut(s,(x,2.10+(j%3)*.06,zz),(x,2.13+(j%3)*.06,zz),.164,'gold' if j%3==0 else 'dark',12)
    paper_lantern(s,x-side*.78,2.92,z-1.33,.64)
def building(s,side,k):
    street=13.8+rng.uniform(0,1.9); w=rng.uniform(10,16); depth=rng.uniform(13,18)
    x=side*(street+w/2); h=rng.uniform(25,63); tall=rng.uniform(15,42); podium=rng.uniform(6.8,9.6)
    theme=0 if s/L<.30 else (1 if s/L<.64 else 2)
    body=['facade','facadeC','facadeB'][(k+theme)%3]; neon=['cyan','rose','gold','lav'][(k+int(side)+2)%4]
    def block(x0,y,z,ww,hh,dd,m):box(s,x0,y,z,ww,hh,dd,m)
    group('Block_%02d_%s'%(k,'E' if side>0 else 'W'))
    # The podium stops behind the display rooms, leaving a real bay below the tower.
    block(x+side*.81,(podium-1)/2,0,w-1.62,podium+1,depth,'basalt')
    block(x,podium*.5+2.14,0,w,podium-4.28,depth,'basalt')
    for end in [-1,1]:block(side*(street+.73),2.1,end*depth*.485,1.68,4.43,depth*.031,'concrete')
    block(x,podium-.15,0,w+.72,.49,depth+.78,'metal')
    is_works=theme==2 and k%3!=0
    if is_works: h*=.43; tall*=.30
    block(x,podium+h/2,0,w,h,depth,'basalt' if is_works else body)
    shift=side*rng.uniform(.65,2)
    block(x+shift,podium+h+tall/2,1,w*.70,tall,depth*.72,'steel' if is_works else body)
    for y in [podium+2+i*4.2 for i in range(int(h/4.2))]:
        block(x,y,0,w+.38,.22 if theme!=2 else .37,depth+.31,'steel')
    block(x+shift,podium+h+tall,1,w*.76,.65,depth*.76,'metal')
    for z in [-depth*.45,depth*.45]:
        block(side*(street-.16),podium+h*.48,z,.48,h*.94,.54,'oxide' if k%5==0 else 'steel')
        if k%3==0:block(side*(street-.43),podium+h*.52,z,.08,h*.82,.11,neon)
    for j in range(3):
        zz=(j-1)*depth*.31; front=side*(street-.10)
        shutter=is_works or (j==2 and k%3==1)
        screen=front+side*(.07 if shutter else 1.38)
        face_sign(s,screen,2.14,zz,depth*.298,3.66,'shutter' if shutter else ['room_noodle','room_records','room_repair','room_store'][(k+theme)%4],-side,0)
        block(side*(street+.57),.36,zz,2.1,.3,depth*.30,'walk')
        if not shutter:
            block(side*(street+.74),3.93,zz,1.58,.14,depth*.30,'concrete')
            block(side*(street+.65),3.83,zz,.11,.055,depth*.20,'gold' if k%2 else 'cyan')
            block(side*(street+.56),.91,zz,.63,.74,depth*.25,'dark')
            for v in range(5):
                block(side*(street+.45),1.39+(v%2)*.10,zz+(v-2)*.51,.32,.26+(v%2)*.15,.31,'metal' if v%3 else 'oxide')
        for v in [-.32,0,.32]:block(front-side*.18,2.32,zz+v*depth*.29,.13,3.6,.092,'metal')
        block(front-side*.19,1.08,zz,.11,.15,depth*.29,'steel')
    block(side*(street-.68),4.42,0,1.64,.24,depth+.2,'dark')
    block(side*(street-1.51),4.41,0,.07,.095,depth-.4,neon)
    face_sign(s,side*(street-.25),5.77,0,depth*.82,2.1,shops[(k+theme)%5],-side,0)
    # Angled blade screens are readable from an approaching vehicle.
    if k%3!=2 and not is_works:
        width=(6.4 if k%4 else 8.8); height=width*1.50
        bx=side*(street-1.45); by=podium+height*.54+(k%3)*1.4; bz=-depth*.39
        strut(s,(side*(street+1.8),by+height*.37,bz),(bx,by+height*.37,bz),.13,'metal')
        strut(s,(side*(street+1),by-height*.35,bz),(bx,by-height*.35,bz),.13,'steel')
        ad=(k+(0 if side==1 else 1)+theme*2)%len(ads)
        face_sign(s,bx,by,bz,width,height,ads[ad],-side*.64,-.82)
        lamps.append([*local(s,side*10.2,4,bz),['aqua','rose','warm','lav'][(k+(0 if side==1 else 2))%4],0])
    # Stacked HVAC service units with grilles, risers and service galleries.
    for j in range(2+k%3):
        zz=depth*.29; y=podium+2.5+j*4.2; xx=side*(street-.56)
        block(xx,y,zz,1.05,1.18,2.21,'concrete')
        for l in range(4):block(xx-side*.55,y-.36+l*.22,zz,.07,.09,1.81,'dark')
    if k%3==1:
        for j in range(2):
            xx=side*(street-.56-j*.30);zz=-depth*.42
            strut(s,(xx,1,zz),(xx,h*.81,zz),.13,'oxide')
    if k%2==0:
        strut(s,(x,h+podium+tall,0),(x,h+podium+tall+6,0),.09,'metal')
        block(x,h+podium+tall+6,0,.21,.27,.21,'red')
    if theme==2 and k%3==0:
        for zz in [-depth*.42,depth*.42]:
            strut(s,(side*(street-1.1),.3,zz),(side*(street+.30),podium,zz+1),.27,'yellow')
    if is_works:
        for j in range(2):
            zz=(j-.5)*depth*.46; xx=x+side*1.8
            ht=podium+h+tall+4+j*5
            strut(s,(xx,ht-4,zz),(xx,ht+7,zz),1.1,'oxide',16)
            for v in (0,2.2,4.4,6.6):strut(s,(xx,ht+v,zz),(xx,ht+v+.25,zz),1.21,'metal',16)
            a=local(s,xx,ht+7,zz)
            ring=[add(a,(1.09*math.cos(u*math.tau/20),0,1.09*math.sin(u*math.tau/20))) for u in range(20)]
            for u in range(20):polygon('dark',[a,ring[u],ring[(u+1)%20]],(0,1,0),[(0,0),(1,0),(0,1)])
        for z in (-depth*.36,depth*.36):
            strut(s,(side*(street-.44),4.7,z),(side*(street-.44),podium+h*.88,z),.35,'oxide',12)
            for y in [6.3,8,10.7,13.4]:
                strut(s,(side*(street-.44),y,z),(side*(street-.44),y+.18,z),.397,'metal',12)
        for j in range(6):
            zz=(j-2.5)*depth*.12
            block(side*(street-.22),podium+h*.60,zz,.45,h*.68,.20,'metal')
    if theme==0 and k%4==1:
        face_sign(s,side*(street-2.1),podium+9,-depth*.48,3.75,13.2,'beacon' if side<0 else 'beacon2',-side*.26,-.96)
        for j in range(3):
            strut(s,(side*(street+.5),podium+4+j*4,-depth*.48),(side*(street-2.1),podium+4+j*4,-depth*.48),.14,'oxide')
    # Kiosks and vending cabinets down at driver eye level.
    if theme==0:
        if k%3!=1:street_stall(s,side,street,depth,k)
        if k%3==1:
            for j in range(5):
                z=(j-2)*1.81
                paper_lantern(s,side*(street-1.60),3.3+.057*z*z,z,.75)
        for row in range(2):
            z=-depth*.45+row*.53
            loop_tube(s,[(side*(street-.36),.5,z),(side*(street-.36),3.58,z),(side*(street-.36),3.94,z+.34),(side*(street-.36),3.94,z+1.6)],.058,'oxide' if row else 'metal')
    if k%3==1:
        for row in range(3):
            h0=podium+4.0+row*4.2
            block(side*(street-.69),h0,0,1.66,.21,depth*.68,'steel')
            for zz in range(-4,5,2):
                strut(s,(side*(street-1.48),h0,zz),(side*(street-1.48),h0+1.04,zz),.036,'metal')
            block(side*(street-1.48),h0+1.05,0,.07,.07,depth*.66,'metal')
    if k%2==0:
        xx=side*(street-1.17); zz=depth*.29
        block(xx,1.35,zz,1.04,2.32,1.32,'oxide' if k%4==0 else 'dark')
        block(xx-side*.534,1.57,zz,.045,.98,.88,'tealglass')
        for j in range(3):block(xx-side*.56,1.25+j*.27,zz,.025,.04,.72,'lamp')
        block(xx-side*.54,.58,zz,.04,.2,.67,'dark')

# Reject footprints whose rear corners would intrude into a different part of the route.
placed=[]
for side in [-1,1]:
    for k in range(int(L/19.8)):
        s=(k+(0.36 if side==1 else .86))*L/int(L/19.8)
        c=local(s,22*side,0); gap=min(math.hypot(p[0]-c[0],p[2]-c[2]) for p in points)
        if gap<18 or any(math.hypot(p[0]-c[0],p[2]-c[2])<15.7 for p in placed):continue
        building(s,side,k);placed.append(c)

# Background slabs and rooftop pylons form a second, less saturated skyline.
for i in range(440):
    x=rng.uniform(-150,355);z=rng.uniform(-288,285)
    if min(math.hypot(p[0]-x,p[2]-z) for p in points[::4])<44:continue
    w=rng.uniform(10,26);d=rng.uniform(11,24); h=rng.uniform(24,123)
    group('Skyline_%d_%d'%(int(x//70),int(z//75)))
    def bg(xx,y,zz,ww,hh,dd,m):cube_at(m,(xx,y,zz),(1,0,0),(0,0,1),ww,hh,dd)
    bg(x,h*.5-2,z,w,h,d,['facade','facadeB','facadeC'][i%3])
    bg(x,h+4,z,w*.75,12,d*.73,'basalt');bg(x,h+10,z,w*.77,.45,d*.76,'steel')
    if i%4==0:bg(x-w*.45,h*.7,z-d*.507,.2,h*.54,.15,['cyan','rose','lav'][i%3])

# Overhead rail galleries and hanging service lines break up the sky down the straights.
for k in range(28):
    s=L*.328+k*4.6;e=s+4.6;group('Elevated_transit_%02d'%(k//4))
    for x in [8.8,11.5]:
        beam(local(s,x,8.18),local(e,x,8.18),.49,'steel',8)
        beam(local(s,x,8.78),local(e,x,8.78),.105,'metal',6)
        beam(local(s,x,7.88),local(e,x,7.88),.080,'cyan',6)
    for dz in [0,2.3]:
        box(s+dz,10.15,8.31,0,3.5,.22,.40,'metal')
    if k%4==0:
        box(s,10.4,4.15,0,.68,8.3,1.05,'oxide')
        strut(s,(10.4,6,0),(8.7,8.15,0),.27,'yellow')
for k in range(20):
    s=L*.704+k*5.6;e=s+5.6;group('Steam_distribution_%02d'%(k//5))
    for x,h,r,m in [(-10.8,4.66,.40,'oxide'),(-10.52,5.32,.20,'metal')]:
        a,b=local(s,x,h),local(e,x,h)
        beam(a,b,r,m,12)
        beam(a,add(a,mul(unit(sub(b,a)),.16)),r+.08,'steel',12)
    if k%2==0:
        box(s,-11,2.36,0,.19,4.72,.27,'steel')
        box(s,-10.72,4.2,0,1.01,.17,.44,'yellow')
for k,pct in enumerate([.064,.136,.213,.335,.414,.55,.692,.805,.922]):
    s=pct*L; group('Overhead_gallery_%02d'%k); y=12+(k%3)*2.5
    for side in [-1,1]:
        box(s,side*11.1,y*.5,0,.72,y,1.05,'concrete')
        strut(s,(side*11,y-3,0),(side*7.6,y,0),.25,'oxide')
    box(s,0,y,0,25,.6,3.8,'steel');box(s,0,y+3.02,0,25,.38,3.8,'basalt')
    box(s,0,y+1.5,0,24,2.65,3.15,'tealglass')
    for j in range(12):
        x=-12+j*2
        strut(s,(x,y+.3,-1.72),(x+1.9,y+2.91,-1.72),.085,'metal')
    box(s,0,y-.36,-1.8,21,.12,.12,'cyan' if k%2 else 'gold')
    if k in [1,3,5,7]:
        for row in range(3):
            pp=[local(s,-13+j*2.6,y-2.6+2*((j-5)/5)**2,row*.54-5) for j in range(11)]
            for a,b in zip(pp,pp[1:]):beam(a,b,.042,'dark',5)
for k,pct in enumerate([0,1/3,2/3]):
    s=L*pct+(.0 if k else 20); group('Sector_portal_%d'%k)
    for side in (-1,1):
        box(s,side*9.25,4,0,.55,8,1.1,'oxide' if k==0 else 'steel')
        strut(s,(side*9.25,6,0),(side*6.9,8.55,0),.25,'metal')
    box(s,0,8.65,0,19.4,.38,1.1,'dark')
    face_sign(s,0,8.58,-.63,8.7,2.17,'finish' if k==0 else 'sector'+str(k),0,-1)
    for side in (-1,1):
        for j in range(3):box(s,side*(5.0+j*.81),8.6,-.59,.46,.22,.12,'cyan')

group('City_foundation')
cube_at('basalt',(60,-2.55,0),(1,0,0),(0,0,1),850,1.4,900)

# Pearl Arcade. Suspended crescents, enamel ribs and a three-dimensional koi sign.
for index,s in enumerate([32,40,59,75,109]):
    group('Pearl_arcade_%d'%index)
    for side in (-1,1):
        for offset in [-.36,.36]:
            path=[]
            for j in range(19):
                a=j*math.pi*.5/18
                path.append((side*(10.62-6.50*(1-math.cos(a))),4.05+7.46*math.sin(a),offset))
            loop_tube(s,path,.15,'oxide')
            if offset<0:loop_tube(s,[(x-side*.11,y-.12,z-.13) for x,y,z in path],.056,'rose' if side<0 else 'cyan')
        for j in range(0,19,3):
            a=j*math.pi*.5/18;x=side*(10.62-6.50*(1-math.cos(a)));y=4.05+7.46*math.sin(a)
            strut(s,(x,y,-.4),(x,y,.4),.092,'metal')
        box(s,side*10.62,2.16,0,.43,4.32,.95,'oxide')
    for j in range(3):
        path=[(-11+k*1.1,11.01+(k-10)**2*.024+j*.28,j*.42-1) for k in range(21)]
        loop_tube(s,path,.036,'dark')
    if index in (1,4):
        for j in range(8):
            x=-9.8+j*2.8
            paper_lantern(s,x,10.35+(x*.1)**2*.91,-.77,.62)

def neon_sculpture(s,side,x,y,z,shape,colour,r):
    # Shape is drawn on a cantilevered sign facing oncoming traffic.
    pts=[(x+side*u,y+v,z+.24*u) for u,v in shape]
    loop_tube(s,pts,r*1.9,'oxide')
    loop_tube(s,[(a,b,c-.12) for a,b,c in pts],r,colour)
for i,s in enumerate([24,95]):
    side=-1 if i==0 else 1;x=side*11.9;y=9.0
    group('Koi_lantern_%d'%i)
    shape=[(-2.7,-.60),(-2.08,.28),(-1.05,.96),(.13,1.19),(1.43,.88),(2.37,.30),(2.64,-.15),(2.04,-.58),(.90,-.73),(-.55,-.52),(-1.70,-.60),(-3.35,-1.51),(-3.03,-.50),(-3.65,.66),(-2.7,-.60)]
    neon_sculpture(s,side,x,y,0,shape,'rose' if i==0 else 'gold',.082)
    for part in [[(-.55,1.08),(-1.04,1.85),(.16,1.54),(.91,1.03)],[(.79,-.63),(.05,-1.39),(-.27,-.53)],[(1.31,.87),(.91,.28),(1.03,-.48)]]:
        neon_sculpture(s,side,x,y,0,part,'gold',.051)
    neon_sculpture(s,side,x,y,0,[(1.82+.115*math.cos(a*math.pi/8),.32+.115*math.sin(a*math.pi/8)) for a in range(17)],'cyan',.046)
    strut(s,(side*15,y,1.1),(x,y,0),.16,'steel')
    lamps.append([*local(s,x,6.3), 'rose' if i==0 else 'warm',0])

# Street drains, industrial signal masts and diagonal hazard shields.
for k in range(50):
    s=k*L/50+5; group('Kerb_services_%02d'%(k//5))
    side=1 if k%2==0 else -1
    box(s,side*7.62,.016,0,.42,.027,1.28,'dark')
    for j in range(9):box(s,side*7.62,.037,-.54+j*.132,.38,.023,.035,'metal')
    if s>.66*L and k%3!=0:
        for offset in [-.42,.42]:
            strut(s,(side*9.1,.2,offset),(side*9.1,5.8,offset),.12,'yellow')
        for j in range(5):
            strut(s,(side*9.12,.55+j, -.4),(side*9.12,1.43+j,.4),.058,'steel')
        box(s,side*9.1,5.95,0,.42,.38,1.14,'dark')
        box(s,side*9.1,5.94,-.59,.28,.18,.055,'red')

s=48;group('Vesper_corner')
face_sign(s,11.9,11.5,0,6.65,10,'vesper',-.34,-1)
for x in [9.12,14.62]:
    strut(s,(x,6.4,1.2),(x,16.7,1.2),.13,'steel')
    strut(s,(x,6.9,1.2),(x+1.3,9.4,1.2),.11,'oxide')
lamps.append([*local(s,10,5.9),'rose',0])

# A two-car automated metro waiting on the elevated guideway.
for carriage,s in enumerate([L*.379+19,L*.379+30]):
    group('Quayside_metro_%d'%carriage)
    x=10.14; floor=8.95
    ends=[]
    for z,w,top in [(-5.48,1.07,2.49),(-4.69,1.40,3.01),(-3.84,1.45,3.10),(3.84,1.45,3.10),(4.82,1.37,2.99),(5.48,1.06,2.49)]:
        ends.append([local(s,x+xx,floor+h,z) for xx,h in [(-w*.87,0),(-w,.31),(-w,top-.43),(-w*.79,top),(w*.79,top),(w,top-.43),(w,.31),(w*.87,0)]])
    center=local(s,x,floor+1.5)
    for a,b in zip(ends,ends[1:]):
        for i in range(8):
            q=[a[i],a[(i+1)%8],b[(i+1)%8],b[i]]
            polygon('metal' if i in (0,1,5,6) else 'steel',q,sub(q[0],center))
    for face in [ends[0],ends[-1]]:
        for j in range(1,7):polygon('tealglass',[face[0],face[j],face[j+1]],sub(face[0],center),[(0,0),(1,0),(1,1)])
    for side in (-1,1):
        box(s,x+side*1.452,floor+.69,0,.03,.38,7.65,'oxide')
        for j in range(7):
            z=-3.42+j*1.14
            box(s,x+side*1.457,floor+1.83,z,.042,1.07,.94,'dark')
            box(s,x+side*1.483,floor+1.85,z,.022,.88,.78,'warmglass' if j%3 else 'tealglass')
            box(s,x+side*1.500,floor+2.24,z,.018,.039,.72,'gold')
        box(s,x+side*1.443,floor+.94,0,.033,.075,7.83,'cyan')
        box(s,x+side*.83,floor+.49,-5.50,.37,.13,.038,'lamp')
    for z in [-2.86,2.86]:box(s,x,floor+3.17,z,1.42,.28,1.38,'dark')

# Banks of refractory furnaces face the descent. Each one has a riveted mantle,
# concentric inspection decks, hot ceramic slots and an overhead exhaust duct.
for i,s in enumerate([L*.762,L*.815,L*.861]):
    group('Kiln_%d'%i);sgn=-1 if i!=1 else 1; x=sgn*13.64
    levels=[(1.2,2.03),(2.5,2.41),(6.4,2.58),(8.16,2.21),(9.72,1.17),(12.,.96)]
    for (ya,ra),(yb,rb) in zip(levels,levels[1:]):
        for j in range(24):
            a=j*math.tau/24;b=(j+1)*math.tau/24
            q=[local(s,x+r*math.cos(t),h,r*math.sin(t)) for h,r,t in [(ya,ra,a),(ya,ra,b),(yb,rb,b),(yb,rb,a)]]
            polygon('oxide' if ya<8 else 'steel',q,sub(q[0],local(s,x,ya,0)))
    for h,r in [(2.58,2.49),(5.45,2.60),(6.55,2.59),(7.87,2.35),(9.85,1.17)]:
        loop_tube(s,[(x+r*math.cos(j*math.tau/32),h,r*math.sin(j*math.tau/32)) for j in range(33)],.104,'metal')
    for j in range(18):
        a=j*math.tau/18
        for v in [-.035,.035]:
            strut(s,(x+2.59*math.cos(a+v),3.1,2.59*math.sin(a+v)),(x+2.65*math.cos(a+v),4.94,2.65*math.sin(a+v)),.049,'gold')
    loop_tube(s,[(x,11.9,0),(x,13.3,0),(x+sgn*.5,13.9,0),(x+sgn*1.3,14.1,0),(x+sgn*5,14.1,0)],.72,'steel')
    lamps.append([*local(s,sgn*10.6,4.55),'warm',0])
manifest=[]
with (BUILD/'mesh.bin').open('wb') as f:
    for name,sections in groups.items():
        surf=[]
        for mat,streams in sections.items():
            spans=[]
            for stream in streams:
                spans.append([f.tell(),len(stream)*stream.itemsize]);stream.tofile(f)
            surf.append([mat,spans])
        manifest.append([name,surf])
(BUILD/'manifest.json').write_text(json.dumps({'mats':materials,'nodes':manifest},separators=(',',':')))
(ROOT/'assets/course.json').write_text(json.dumps({'length':L,'points':[[round(q,4) for q in p] for p in points],'lights':lamps},separators=(',',':')))
print(f'{L:.1f} metres, {len(placed)} roadside blocks, {len(groups)} mesh groups')
