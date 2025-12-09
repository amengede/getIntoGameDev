@group(0) @binding(0) var<uniform> color: vec4<f32>;
@group(1) @binding(0) var<uniform> model: mat4x4<f32>;
@group(2) @binding(0) var<uniform> view_projection: mat4x4<f32>;

struct Vertex {
    @location(0) position: vec3<f32>,
    @location(1) tex_coord: vec2<f32>,
    @location(2) normal: vec3<f32>,
};

struct VertexPayload {
    @builtin(position) position: vec4<f32>,
    @location(0) normal: vec3<f32>,
};

@vertex
fn vs_main(vertex: Vertex) -> VertexPayload {

    var out: VertexPayload;
    out.position = view_projection * model * vec4<f32>(vertex.position, 1.0);
    out.normal = (model * vec4<f32>(vertex.normal, 0.0)).xyz;
    return out;
}

@fragment
fn fs_main(in: VertexPayload) -> @location(0) vec4<f32> {
    var sun_direction: vec3<f32> = normalize(vec3<f32>(1.0, 1.0, -1.0));
    var light_strength: f32 = max(0.0, dot(in.normal, sun_direction));
    return vec4<f32>(light_strength * color.rgb, 1.0);
}