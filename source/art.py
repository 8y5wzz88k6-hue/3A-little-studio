"""Original wayfinding, screen prints and cladding, rasterized for the track."""
from pathlib import Path
import math
import random
from PIL import Image, ImageDraw, ImageFont, ImageFilter

OUT = Path(__file__).resolve().parents[1] / 'assets' / 'signs'
FONT = Path('C:/Windows/Fonts')
rng = random.Random(73)

def font(file, n):
    return ImageFont.truetype(str(FONT / file), n)

def word(d, xy, s, n, color, face='bahnschrift.ttf'):
    d.text(xy, s, font=font(face, n), fill=color, anchor='lt')

def bars(d, x, y, h, color):
    for i in range(35):
        w = rng.choice([1, 2, 2, 4, 6])
        d.rectangle((x,y,x+w,y+h),fill=color)
        x += w + 3

def poster(name, base, ink, bright, title, cn, index):
    w,h=512,768
    im=Image.new('RGB',(w,h),base)
    d=ImageDraw.Draw(im)
    for y in range(h):
        k=(0.5+0.5*math.sin(y/h*math.pi))*.21
        d.line((0,y,w,y),fill=tuple(int(a*(1-k)+b*k) for a,b in zip(base,bright)))
    for x in range(28,w,38):
        for y in range(92,h-100,38):
            d.point((x,y),fill=ink)
    word(d,(27,22),'PELAGIC   /   CITY EDITIONS',17,ink,'consolab.ttf')
    word(d,(426,18),f'0{index+1}',40,ink,'ARIALNB.TTF')
    d.line((26,61,486,61),fill=ink,width=2)
    if index==0: # engraved jellyfish and looping tentacles
        for j in range(65):
            t=j/64; pts=[]
            for i in range(95):
                a=math.pi*i/94
                pts.append((256+math.cos(a)*(147-23*t),313-math.sin(a)*(153-119*t)+12*math.cos(a*6)*t))
            d.line(pts,fill=tuple(int(a*(1-t)+b*t) for a,b in zip(bright,ink)),width=2)
        for j in range(27):
            x=125+j*10
            d.line([(x+math.sin(t*.09+j*.55)*(9+t*.19)+t*.14,305+t) for t in range(0,176-j%4*16,2)],fill=bright,width=2)
    elif index==1: # topographic wave stack
        for j in range(67):
            pts=[]
            for i in range(213):
                x=43+i*2
                y=258+j*2.45+57*math.sin(i*.031+j*.041)+39*math.cos(i*.012+j*.083)
                pts.append((x,y))
            d.line(pts,fill=bright if j%5 else ink,width=2)
    elif index==2: # celestial orbit diagram
        for j in range(46):
            r=95+j*.9
            pts=[(256+math.cos(a*.039)*r+math.sin(a*.039)*j*.65,298+math.sin(a*.039)*r*.78+j*.43) for a in range(163)]
            d.line(pts,fill=ink if j%4==0 else bright,width=2)
        for j in range(9):
            d.line([(256+179*math.cos(a*.03)+38*math.sin(a*.03),309+51*math.sin(a*.03)-74*math.cos(a*.03)+j*2) for a in range(212)],fill=bright,width=2)
    else: # folding ribbon
        for j in range(61):
            d.line([(69+j*2,411),(203+j*2,173),(340+j,313),(441-j,416),(288-j,276),(153+j,439)],fill=bright if j%3 else ink,width=2)
    word(d,(26,494),title,91 if len(title)<7 else 75,ink,'impact.ttf')
    word(d,(30,605),cn,39,bright,'msyhbd.ttc')
    d.line((28,681,484,681),fill=ink,width=2)
    bars(d,30,702,29,ink)
    word(d,(212,704),'TIDELINE   //   '+str(26+index),21,ink,'consolab.ttf')
    im.save(OUT/(name+'.png'))

def neon_marquee(name,headline,caption,cold,hot):
    size=(1080,252); bg=Image.new('RGB',size,(15,18,28)); d=ImageDraw.Draw(bg)
    for y in range(0,252,6):d.line((0,y,1080,y),fill=(29,30,41),width=1)
    tubes=Image.new('L',size); mask=ImageDraw.Draw(tubes)
    face=font('msyhbd.ttc',108)
    mask.text((25,24),headline,font=face,fill=0,stroke_width=3,stroke_fill=255,anchor='lt')
    mask.line((30,157,1047,157),fill=170,width=3)
    for x in [845,906,967]:
        mask.line([(x,38),(x+29,77),(x,116)],fill=245,width=5,joint='curve')
    def light(layer,color,factor,blur):
        nonlocal bg
        alpha=layer.filter(ImageFilter.GaussianBlur(blur)) if blur else layer
        bg=Image.composite(Image.new('RGB',size,color),bg,alpha.point(lambda a:int(a*factor)))
    light(tubes,cold,.92,13); light(tubes,cold,.92,5);light(tubes,hot,1,0)
    d=ImageDraw.Draw(bg);word(d,(34,182),caption,40,hot,'ARIALNB.TTF')
    bg.save(OUT/(name+'.png'))

# Inset shop interiors, illustrated at street scale with receding ceilings and stocked shelves.
for n,(name,heading,bg,light) in enumerate([
    ('records','PHASE   RECORDS',(29,27,40),(233,121,151)),
    ('spares','COIL   PARTS',(38,36,37),(222,168,91)),
    ('deli','LOW TIDE   /   24 H',(27,42,43),(111,201,166))]):
    im=Image.new('RGB',(768,320),bg); d=ImageDraw.Draw(im)
    d.rectangle((44,53,723,267),fill=tuple(v+13 for v in bg))
    for xx in range(-200,970,94):
        d.line((xx,0,330+(xx-330)*.67,56),fill=tuple(v+20 for v in bg),width=3)
    for xx in (92,348,605):
        d.rounded_rectangle((xx,30,xx+96,35),radius=2,fill=light)
    for row in range(3):
        yy=122+row*40
        d.rectangle((63,yy,709,yy+4),fill=tuple(int(v*.59) for v in light))
        for col in range(32):
            xx=67+col*20+rng.randint(-2,2)
            ht=rng.randint(12,30); tint=rng.choice([(98,105,108),(158,136,100),(116,151,144),(166,102,95),light])
            if n==0:
                d.rectangle((xx,yy-ht,xx+16,yy-1),fill=tint)
                d.ellipse((xx+4,yy-ht+3,xx+13,yy-ht+12),fill=bg)
            elif n==1:
                d.rounded_rectangle((xx,yy-ht,xx+16,yy),2,fill=tint)
                d.line((xx+3,yy-7,xx+12,yy-7),fill=bg,width=2)
            else:
                d.rectangle((xx+4,yy-ht,xx+11,yy-ht+6),fill=tint)
                d.rounded_rectangle((xx+1,yy-ht+5,xx+14,yy),3,fill=tint)
                d.rectangle((xx+1,yy-12,xx+14,yy-7),fill=bg)
    d.rectangle((30,224,737,288),fill=tuple(v+8 for v in bg))
    d.rectangle((30,223,737,228),fill=light)
    word(d,(54,242),heading,24,light,'ARIALNB.TTF')
    for xx in (524,622): d.rectangle((xx,209,xx+43,223),fill=(69,80,80))
    im.save(OUT/(name+'.png'))

# Narrow beacon, warehouse roller door, municipal maintenance tag and rail insignia.
for name,characters,small,base,ink in [
    ('beacon','潮汐社','TIDE   /   PRESS','#493040','#FFD7BA'),
    ('beacon2','深水港','PORT   /   06','#194750','#B6F9DF')]:
    im=Image.new('RGB',(256,896),base); d=ImageDraw.Draw(im)
    d.rectangle((9,9,246,886),outline=ink,width=3)
    word(d,(28,34),'PORT   06',34,ink,'ARIALNB.TTF')
    for j,ch in enumerate(characters):word(d,(30,137+j*200),ch,177,ink,'msyhbd.ttc')
    word(d,(27,784),small,20,ink,'consolab.ttf')
    bars(d,28,826,19,ink);im.save(OUT/(name+'.png'))
im=Image.new('RGB',(640,320),(66,72,76));d=ImageDraw.Draw(im)
for y in range(7,307,13):
    d.rectangle((11,y,629,y+2),fill=(98,105,105)); d.rectangle((11,y+8,629,y+10),fill=(40,46,49))
for j in range(1700):
    x=rng.randrange(12,628);y=rng.randrange(310)
    d.line((x,y,x+rng.randrange(1,7),y+1),fill=rng.choice([(88,85,78),(52,58,59)]))
d.rectangle((46,62,265,116),fill=(173,137,77));word(d,(60,72),'DEPOT  09',34,(43,45,49),'impact.ttf')
for i in range(5):d.polygon([(385+i*34,219),(399+i*34,219),(375+i*34,258),(361+i*34,258)],fill=(148,123,76))
im.save(OUT/'shutter.png')

posters=[
    ('medusa',(8,55,68),(193,255,202),(72,245,221),'MEDUSA','深 潮 研 究 所'),
    ('phase',(93,12,53),(255,232,179),(255,99,138),'PHASE','相 位 聲 場'),
    ('orbit',(58,30,15),(255,235,167),(255,144,49),'APOGEE','軌 道 交 通'),
    ('fold',(41,27,73),(235,208,255),(168,138,255),'FOLD','折 光 工 業')]
for i,args in enumerate(posters): poster(*args,i)

shop_data=[
    ('market','汐 街 夜 市','LOW TIDE MARKET','E7DED0','F56D53','33272A'),
    ('coil','線 圈 維 修','COIL MOTOR WORKS','E6C795','FF9B43','342D29'),
    ('relay','中 繼 電 台','RELAY  /  88.4 FM','B3F4DF','66DDBE','183739'),
    ('arc','弧 光 劇 場','ARC LIGHT CINEMA','F4CFDE','FF7FB5','492A40'),
    ('transit','港 灣 環 線','HARBOR TRANSIT','E7EEDE','B4D158','334143'),
    ('finish','潮 汐 環 線','TIDELINE  /  CIRCUIT','FFEDD4','FC764F','292E35'),
    ('sector0','汐 街  /  01','01   MARKET STRAIGHT','F0E9DD','FF775C','30323C'),
    ('sector1','軌 道  /  02','02   ORBIT VIADUCT','CEF2ED','64E8CE','273A43'),
    ('sector2','機 廠  /  03','03   FOUNDRY BEND','F5EAC9','FFBB57','393435')]
for name,cn,en,fg,accent,bg in shop_data:
    fg,accent,bg=['#'+s for s in (fg,accent,bg)]
    im=Image.new('RGB',(960,240),bg); d=ImageDraw.Draw(im)
    d.rectangle((0,0,13,240),fill=accent)
    d.line((39,24,915,24),fill=accent,width=3)
    word(d,(42,41),cn,75,fg,'msyhbd.ttc')
    word(d,(45,145),en,48,accent,'ARIALNB.TTF')
    for k in range(3):
        x=792+k*32
        d.polygon([(x,62),(x+16,62),(x+43,91),(x+16,120),(x,120),(x+26,91)],fill=accent)
    d.line((40,211,916,211),fill=fg,width=1)
    im.save(OUT/(name+'.png'))

for spec in [
    ('market','汐 街 夜 市','LOW TIDE   /   NIGHT MARKET',(232,13,84),(255,166,178)),
    ('coil','線 圈 工 坊','COIL MOTOR WORKS',(255,86,12),(255,192,80)),
    ('relay','港 口 電 台','HARBOR RADIO   /   88.4',(1,192,168),(137,255,226)),
    ('arc','弧 光 映 畫','ARC LIGHT   /   CINEMA',(158,32,220),(255,144,233)),
    ('transit','港 灣 軌 道','HARBOR TRANSIT AUTHORITY',(21,116,246),(123,217,255))]:
    neon_marquee(*spec)
