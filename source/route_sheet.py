"""Draw a route sheet from the same samples and block geometry as the game."""
import json
import math
import struct
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

root=Path(__file__).resolve().parents[1]
course=json.loads((root/'assets/course.json').read_text())
manifest=json.loads((root/'source/intermediate/manifest.json').read_text())
pts=course['points']; width,height=1440,960
img=Image.new('RGB',(width,height),'#112029')
d=ImageDraw.Draw(img)
fonts=Path('C:/Windows/Fonts')
def label(x,y,text,sz,fill='#dbebe6',face='bahnschrift.ttf'):
    d.text((x,y),text,font=ImageFont.truetype(str(fonts/face),sz),fill=fill,anchor='lt')
def map_pt(x,z):return (305+x*1.98,501+z*1.98)
def clamprect(x,y):return 52<x<984 and 155<y<852
for x in range(50,990,44):d.line((x,152,x,852),fill='#1b2d36')
for y in range(154,854,44):d.line((50,y,984,y),fill='#1b2d36')
with (root/'source/intermediate/mesh.bin').open('rb') as f:
    for name,surfaces in manifest['nodes']:
        if not name.startswith('Block_'):continue
        offset,length=surfaces[0][1][0]
        f.seek(offset)
        vals=struct.unpack('<72f',f.read(288))
        footprint=list({map_pt(*[round(vals[i+q],3) for q in (0,2)]) for i in range(0,72,3)})
        cx=sum(x for x,y in footprint)/len(footprint);cy=sum(y for x,y in footprint)/len(footprint)
        footprint.sort(key=lambda v:math.atan2(v[1]-cy,v[0]-cx))
        if all(clamprect(x,y) for x,y in footprint):
            d.polygon(footprint,fill='#203640',outline='#36505a',width=1)
xy=[map_pt(p[0],p[2]) for p in pts]; n=len(pts)
accents=['#ff8b68','#73e0d1','#eebc70']
d.line(xy+[xy[0]],fill='#0c171d',width=20,joint='curve')
for i,c in enumerate(accents):
    line=(xy+[xy[0]])[round(i*n/3):round((i+1)*n/3)+1]
    d.line(line,fill=c,width=8,joint='curve')
    for t in [i/3+.095,i/3+.235]:
        k=int(t*n)%n;x,y=xy[k];xx,yy=xy[(k+1)%n]
        norm=math.hypot(xx-x,yy-y);fx=(xx-x)/norm;fy=(yy-y)/norm
        d.polygon([(x+fx*8,y+fy*8),(x-fx*6-fy*5,y-fy*6+fx*5),(x-fx*6+fy*5,y-fy*6-fx*5)],fill='#f4f1df')
for i,(dx,dy) in enumerate([(-81,9),(18,-23),(18,2)]):
    x,y=xy[round(n*i/3)]
    d.ellipse((x-8,y-8,x+8,y+8),fill='#112029',outline=accents[i],width=3)
    target=(x+dx,y+dy)
    d.line((x,y,*target),fill=accents[i],width=1)
    label(target[0]-23 if dx<0 else target[0]+2,target[1]-16,['S/F','CP 1','CP 2'][i],18,accents[i],'consolab.ttf')
label(48,36,'TIDELINE',70,'#e5ece4','ARIALNB.TTF')
label(365,56,'潮汐环线',39,'#e5ece4','msyhbd.ttc')
label(51,114,'HARBOR DISTRICT     /     CIRCUIT PLAN',20,'#a5baba','consola.ttf')
d.line((50,147,1390,147),fill='#526369',width=1)
d.line((1015,185,1015,844),fill='#40545b',width=1)
label(1060,194,'全长',21,'#a5baba','msyh.ttc')
label(1057,239,'893.4',76,'#e5ece4','ARIALNB.TTF');label(1265,284,'m',28)
for i,(cn,en) in enumerate([('汐街商区','MARKET STRAIGHT'),('轨道高架','ORBIT VIADUCT'),('铸造厂区','FOUNDRY BEND')]):
    y=365+i*91
    d.rectangle((1061,y+1,1066,y+48),fill=accents[i])
    label(1082,y+1,f'0{i+1}',26,accents[i],'consolab.ttf')
    label(1133,y,cn,25,'#e5ece4','msyhbd.ttc')
    label(1083,y+34,en,17,'#a5baba','consola.ttf')
label(1060,679,'路面高程',21,'#e5ece4','msyh.ttc')
label(1290,683,'8.5 m',20,accents[1],'consola.ttf')
prof=[(1060+i/(n-1)*319,795-p[1]*7.8) for i,p in enumerate(pts)]
d.line((1060,795,1379,795),fill='#4a6269',width=2)
d.line(prof,fill=accents[1],width=3)
label(1060,812,'0 m',16,'#9fb4b5','consola.ttf')
label(1310,812,'893 m',16,'#9fb4b5','consola.ttf')
label(66,183,'N',18,'#c6d3cb','consolab.ttf')
d.polygon([(71,210),(65,230),(71,225),(77,230)],fill='#acbdb9')
d.line((50,874,1390,874),fill='#526369')
label(51,899,'S/F   起终点',19,'#bfcecb','msyh.ttc')
label(258,899,'CP   分段检查点',19,'#bfcecb','msyh.ttc')
label(1049,899,'KESTREL   /   R9',24,'#b7cbc9','ARIALNB.TTF')
img.save(root/'preview'/'route.png')
