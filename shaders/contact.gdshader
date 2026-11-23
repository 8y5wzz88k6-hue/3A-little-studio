shader_type spatial;
render_mode unshaded, cull_disabled, shadows_disabled, depth_draw_never;
void fragment(){
    vec2 p=(UV-.5)*vec2(3.26,5.75);
    vec2 outside=max(abs(p)-vec2(.68,1.69),vec2(0.));
    float belly=exp(-dot(outside*vec2(3.1,2.6),outside*vec2(3.1,2.6)));
    vec2 tire=(abs(p)-vec2(1.02,1.46))*vec2(5.7,3.7);
    float footprint=exp(-dot(tire,tire));
    ALBEDO=vec3(.004,.008,.010);
    ALPHA=min(.87,belly*.67+footprint*.63);
}
