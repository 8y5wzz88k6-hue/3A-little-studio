extends Control

var race
var map_only := false
var sans := SystemFont.new()
var numeric := SystemFont.new()
var chinese := SystemFont.new()
var route_line := PackedVector2Array()
var map_min := Vector2.ZERO
var map_scale := 1.0
const INK := Color("#e9f0ea")
const DIM := Color("#b9cacb")
const ICE := Color("#79ebd6")
const ORANGE := Color("#ff805c")
const PLATE := Color(.035,.059,.078,.88)

func _ready():
    sans.font_names = PackedStringArray(["Bahnschrift","Arial"])
    numeric.font_names = PackedStringArray(["Consolas","DejaVu Sans Mono"])
    chinese.font_names = PackedStringArray(["Microsoft YaHei","Noto Sans CJK SC","Arial"])

func label(p: Vector2,txt: String,pt: int,col: Color=INK,font: Font=null):
    draw_string(font if font else sans,p,txt,HORIZONTAL_ALIGNMENT_LEFT,-1,pt,col)

func panel(x: float,y: float,w: float,h: float):
    draw_rect(Rect2(x,y,w,h),PLATE)
    draw_line(Vector2(x,y+h),Vector2(x+w,y+h),Color(.53,.70,.73,.32),1)

func mapped(p: Vector3) -> Vector2:
    return (Vector2(p.x,p.z)-map_min)*map_scale

func _draw():
    if not race or race.points.is_empty():return
    if map_only:
        draw_map(Vector2.ZERO)
        return
    var w := size.x
    var h := size.y
    var x := 32.0
    if not race.in_cockpit:
        panel(x,28,240,63)
        draw_rect(Rect2(x,28,4,63),ORANGE)
        for i in range(3):
            var dx=x+15+i*8
            draw_colored_polygon(PackedVector2Array([Vector2(dx,63),Vector2(dx+9,43),Vector2(dx+14,43),Vector2(dx+5,63)]),ORANGE)
        label(Vector2(x+57,58),"TIDELINE",27)
        label(Vector2(x+59,78),"潮汐环线  /  港区计时赛",13,DIM,chinese)
        panel(w-267,28,235,82)
        label(Vector2(w-252,51),"LAP  %02d"%race.lap,17,ICE,numeric)
        label(Vector2(w-131,51),"TIME TRIAL",13,DIM)
        label(Vector2(w-254,81),race.lap_string(race.lap_time),28,INK,numeric)
        label(Vector2(w-252,100),"BEST    "+(race.lap_string(race.best_time) if race.best_time>0 else "--:--.---"),13,DIM,numeric)
        draw_map(Vector2(x,h-165))
        var bx := w-225
        var by := h-127
        panel(bx,by,193,99)
        label(Vector2(bx+13,by+23),"KESTREL   /   R9",15,ICE)
        label(Vector2(bx+12,by+73),"%03d"%roundi(absf(race.speed)*3.6),53,INK,numeric)
        label(Vector2(bx+123,by+70),"KM/H",15,DIM)
        for i in 18:
            draw_rect(Rect2(bx+13+i*9.3,by+84,7,4),ICE if float(i)/18.0<absf(race.speed)/53 else Color("#42515a"))
    if not race.started:
        var text := "W / ↑ 起步     A D 转向     H 操作说明"
        var tw := chinese.get_string_size(text,HORIZONTAL_ALIGNMENT_LEFT,-1,16).x
        panel((w-tw)/2-15,h-66,tw+30,38)
        label(Vector2((w-tw)/2,h-41),text,16,INK,chinese)
    if race.notice_time>0:
        var msg: String = race.notification
        var tw := chinese.get_string_size(msg,HORIZONTAL_ALIGNMENT_LEFT,-1,22).x
        panel((w-tw)/2-20,39,tw+40,45)
        label(Vector2((w-tw)/2,69),msg,22,ICE,chinese)
    if race.hold or race.help:
        var center := Vector2(w/2,h/2)
        panel(center.x-181,center.y-107,362,214)
        draw_rect(Rect2(center.x-181,center.y-107,362,3),ORANGE)
        label(center+Vector2(-157,-68),"暂停" if race.hold else "驾驶操作",24,INK,chinese)
        var lines := ["W / ↑  加速       S / ↓  刹车、倒车","A D / ← →  转向       空格  手刹","C  切换视角          R  回到当前赛道","M  引擎静音          P / Esc  暂停","H  开关操作说明"]
        for i in lines.size():
            label(center+Vector2(-157,-35+26*i),lines[i],16,DIM,chinese)

func draw_map(origin: Vector2):
    if route_line.is_empty():
        var bounds := Rect2(Vector2(race.points[0].x,race.points[0].z),Vector2.ZERO)
        for p in race.points: bounds=bounds.expand(Vector2(p.x,p.z))
        map_min=bounds.position
        map_scale=minf(98/bounds.size.x,100/bounds.size.y)
        for i in range(0,race.points.size(),2):route_line.append(mapped(race.points[i]))
        route_line.append(route_line[0])
    panel(origin.x,origin.y,214,137)
    var anchor := origin+Vector2(15,19)
    draw_set_transform(anchor)
    draw_polyline(route_line,Color("#44565f"),5,true)
    draw_polyline(route_line,Color("#9bbbbb"),1.5,true)
    var start := mapped(race.points[0])
    draw_rect(Rect2(start-Vector2(2,2),Vector2(4,4)),ORANGE)
    var p := mapped(race.car.position)
    var f := Vector2(-sin(race.yaw),-cos(race.yaw))
    var side := Vector2(-f.y,f.x)
    draw_colored_polygon(PackedVector2Array([p+f*6,p-f*4+side*4,p-f*4-side*4]),ICE)
    draw_set_transform(Vector2.ZERO)
    var sector := mini(2,int(race.progress/race.distance_total*3))
    label(origin+Vector2(117,39),"SECTOR",12,DIM,numeric)
    label(origin+Vector2(115,75),"0"+str(sector+1),36,ICE,numeric)
    label(origin+Vector2(116,99),["汐街商区","轨道高架","铸造厂区"][sector],16,INK,chinese)
    label(origin+Vector2(117,119),"0.893 KM",12,DIM,numeric)
