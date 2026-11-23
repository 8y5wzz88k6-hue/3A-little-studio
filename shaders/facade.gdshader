shader_type spatial;
uniform vec4 cladding : source_color = vec4(.26,.33,.39,1.);
uniform float seed = 0.;
varying vec3 wp;
void vertex(){wp=(MODEL_MATRIX*vec4(VERTEX,1.)).xyz;}
float rand(vec2 p){return fract(sin(dot(p,vec2(127.1,311.7)))*4375.5453);}
void fragment(){
    vec2 meters=UV;
    vec2 grid=meters/vec2(1.66,3.12);
    vec2 id=floor(grid), f=fract(grid);
    float block=rand(floor(vec2(wp.x+wp.z,0.)*.008)+vec2(seed,2.));
    float noise=rand(id+floor(vec2(wp.x-wp.z,0.)*.014)+vec2(seed,19.));
    float glass=smoothstep(.08,.105,f.x)*(1.-smoothstep(.91,.94,f.x))*smoothstep(.16,.185,f.y)*(1.-smoothstep(.67,.70,f.y));
    float blade=1.-smoothstep(.015,.033,abs(f.y-.72));
    float seam=smoothstep(.004,.023,min(f.x,1.-f.x))*smoothstep(.004,.02,min(f.y,1.-f.y));
    float blind=.81+.19*smoothstep(.15,.52,fract(f.y*16.));
    float lit=smoothstep(.62,.94,noise)*(.45+.55*block);
    vec3 pane=mix(vec3(.034,.077,.100),vec3(.17,.27,.3),noise);
    vec3 glow=mix(vec3(.36,.74,.80),vec3(1.,.63,.33),step(.59,rand(id+vec2(12.,seed))));
    ALBEDO=mix(cladding.rgb*(.76+.23*noise)*(.72+.28*seam)+blade*.048,pane,glass);
    METALLIC=.39+glass*.26; ROUGHNESS=.58-glass*.31;
    EMISSION=glass*blind*(glow*lit*1.16+vec3(.022,.044,.055));
}
