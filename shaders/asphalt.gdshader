shader_type spatial;
uniform sampler2D city_mirror : hint_default_black, filter_linear, repeat_disable;
uniform mat4 mirror_view_projection;
uniform float mirror_on = 0.0;
varying vec3 world_position;
void vertex(){world_position=(MODEL_MATRIX*vec4(VERTEX,1.)).xyz;}
float hash(vec2 p){return fract(sin(dot(p,vec2(13.61,57.19)))*43571.73);}
float noise2(vec2 p){
    vec2 i=floor(p), f=fract(p); f=f*f*(3.-2.*f);
    return mix(mix(hash(i),hash(i+vec2(1,0)),f.x),mix(hash(i+vec2(0,1)),hash(i+vec2(1,1)),f.x),f.y);
}
void fragment(){
    vec2 p=UV;
    float bed=noise2(p*vec2(.35,.20))*.61+noise2(p*.83)*.28+noise2(p*3.37)*.11;
    float wet=smoothstep(.37,.69,bed);
    float grit=noise2(p*44.);
    float track=exp(-pow((abs(p.x)-2.25)*2.2,2.))+exp(-pow((abs(p.x)-5.67)*2.2,2.));
    float seam=smoothstep(.012,.047,abs(fract((p.y+.13*sin(p.x))/18.)-.5)*18.);
    float stone=(grit-.5)*(.33-.23*wet);
    ALBEDO=mix(vec3(.059,.066,.076),vec3(.019,.028,.036),wet)*(.97+stone)*(.67+.33*seam)*(1.-track*.16);
    METALLIC=.17+.16*wet;
    SPECULAR=.70;
    ROUGHNESS=mix(.50,.14,wet)+grit*.035;
    vec4 clip=mirror_view_projection*vec4(world_position,1.);
    vec2 uv=clip.xy/max(.01,clip.w)*vec2(.5,-.5)+.5;
    float flow=noise2(p*vec2(6.,1.15)+vec2(0.,TIME*.08));
    float ripple=sin(p.y*28.+p.x*3.+TIME*1.9)*.2+flow-.5;
    vec2 warp=vec2((noise2(p*vec2(3.,9.))-.5)*.003,ripple*.009)*(1.35-.6*wet);
    vec2 suv=clamp(uv+warp,vec2(.002),vec2(.998));
    vec2 spread=vec2(.0025+.008*(1.-wet),.004+.004*(1.-wet));
    vec3 mirrored=texture(city_mirror,suv).rgb*.46;
    mirrored+=(texture(city_mirror,suv+spread).rgb+texture(city_mirror,suv-spread).rgb)*.27;
    vec2 edge=smoothstep(vec2(0.),vec2(.035),uv)*smoothstep(vec2(0.),vec2(.035),1.-uv);
    float grazing=pow(1.-max(dot(NORMAL,VIEW),0.),1.8);
    float fleck=.67+.33*smoothstep(.18,.76,flow);
    EMISSION=mirrored*mirror_on*edge.x*edge.y*step(.01,clip.w)*(.023+.42*wet)*(.13+.87*grazing)*fleck;
}
