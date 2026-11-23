extends Control

var race
var digits := SystemFont.new()
const WHITE := Color("#e6efe9")
const TEAL := Color("#68dcc7")
const AMBER := Color("#ffb46a")
const MUTED := Color("#89a6ab")

func _ready():
    digits.font_names=PackedStringArray(["Consolas","DejaVu Sans Mono"])
    digits.font_weight=700

func write(at: Vector2, value: String, height: int, color: Color):
    draw_string(digits,at,value,HORIZONTAL_ALIGNMENT_LEFT,-1,height,color)

func _draw():
    if not race:return
    draw_rect(Rect2(Vector2.ZERO,size),Color("#0a171c"))
    var velocity:float=absf(race.speed)
    var gear:=mini(5,int(velocity/9.0))
    var revs:=clampf(.18+(velocity-gear*9.)/10.,.18,1.)
    for i in 25:
        var live:=TEAL if i<19 else AMBER
        draw_rect(Rect2(15+i*28,11,22,10),live if i/25.<revs else Color("#244249"))
    write(Vector2(18,50),"KESTREL  /  R9",22,MUTED)
    write(Vector2(20,151),"%03d"%roundi(velocity*3.6),111,WHITE)
    write(Vector2(231,149),"KM/H",25,TEAL)
    draw_line(Vector2(327,39),Vector2(327,154),Color("#365058"),3)
    write(Vector2(351,60),"GEAR",22,MUTED)
    var gear_text: String="R" if race.speed<-.12 else ("N" if velocity<.12 else str(gear+1))
    write(Vector2(352,146),gear_text,88,AMBER)
    write(Vector2(475,67),"LAP  %02d"%race.lap,31,WHITE)
    write(Vector2(475,117),race.lap_string(race.lap_time),32,TEAL)
    draw_line(Vector2(17,166),Vector2(711,166),Color("#345158"),2)
    write(Vector2(18,191),"PELAGIC MOTORSPORT",19,MUTED)
    write(Vector2(475,191),"BEST "+(race.lap_string(race.best_time) if race.best_time>0 else "--:--.---"),19,MUTED)
