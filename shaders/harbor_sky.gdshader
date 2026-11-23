shader_type sky;
uniform sampler2D street_panorama : filter_linear_mipmap, repeat_enable;
void sky(){
    vec3 d=normalize(EYEDIR);
    if(AT_CUBEMAP_PASS){
        vec2 uv=vec2(atan(d.z,d.x)/TAU+.5,acos(clamp(d.y,-1.,1.))/PI);
        COLOR=texture(street_panorama,uv).rgb*.85;
    }else{
        float horizon=pow(1.-abs(d.y),3.);
        COLOR=mix(vec3(.006,.006,.025),vec3(.064,.036,.092),horizon);
    }
}
