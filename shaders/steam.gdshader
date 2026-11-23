shader_type spatial;
render_mode unshaded, shadows_disabled, cull_disabled, depth_draw_never;
uniform vec4 tint : source_color;
uniform float offset;
float hash(vec2 p){return fract(sin(dot(p,vec2(39.34,117.81)))*34781.37);}
float noise2(vec2 p){
    vec2 i=floor(p),f=fract(p);f=f*f*(3.-2.*f);
    return mix(mix(hash(i),hash(i+vec2(1,0)),f.x),mix(hash(i+vec2(0,1)),hash(i+1.),f.x),f.y);
}
void vertex(){
    MODELVIEW_MATRIX=VIEW_MATRIX*mat4(INV_VIEW_MATRIX[0],INV_VIEW_MATRIX[1],INV_VIEW_MATRIX[2],MODEL_MATRIX[3]);
}
void fragment(){
    float h=1.-UV.y;
    vec2 p=vec2(UV.x*4.,UV.y*4.+TIME*.35+offset);
    float cloud=noise2(p)*.56+noise2(p*2.17)*.29+noise2(p*4.03)*.15;
    float drift=.11*sin(h*5.+TIME*.44+offset)*h;
    float radius=.075+.41*h;
    float plume=1.-smoothstep(radius*.14,radius,abs(UV.x-.50-drift+(cloud-.5)*.21));
    ALBEDO=tint.rgb;
    ALPHA=plume*smoothstep(.25,.70,cloud)*smoothstep(0.,.13,h)*(1.-smoothstep(.40,1.,h))*.36;
}
