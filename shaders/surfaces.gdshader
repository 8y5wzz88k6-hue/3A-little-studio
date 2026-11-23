shader_type spatial;
uniform vec4 coating : source_color;
uniform float metalness;
uniform float finish;
varying vec3 wp;
void vertex(){wp=(MODEL_MATRIX*vec4(VERTEX,1.)).xyz;}
float hash(vec2 p){return fract(sin(dot(p,vec2(41.31,19.71)))*38192.78);}
float grain(vec2 p){
    vec2 i=floor(p), f=fract(p); f=f*f*(3.-2.*f);
    return mix(mix(hash(i),hash(i+vec2(1,0)),f.x),mix(hash(i+vec2(0,1)),hash(i+vec2(1,1)),f.x),f.y);
}
void fragment(){
    vec2 uv=UV+wp.xz*.031;
    float pores=grain(uv*71.);
    float rain=grain(uv*vec2(5.2,.37))*.58 + grain(uv*vec2(17.,1.7))*.42;
    float marks=smoothstep(.70,.90,rain);
    float grime=1.-smoothstep(.15,1.65,wp.y);
    ALBEDO=coating.rgb*(.82+pores*.21+rain*.12)*(1.-.31*marks)*(1.-.19*grime);
    ROUGHNESS=clamp(finish+(pores-.5)*.12+marks*.13,.05,.95);
    METALLIC=metalness;
}
