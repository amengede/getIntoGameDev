@group(0) @binding(0) var myTexture: texture_2d<f32>;
@group(0) @binding(1) var mySampler: sampler;
@group(1) @binding(0) var<uniform> model: mat4x4<f32>;
@group(2) @binding(0) var<uniform> view_projection: mat4x4<f32>;
//@group(3) @binding(0) var<uniform> bone_transforms: array<mat4x4<f32>, 128>;

struct Vertex {
    @location(0) position: vec3<f32>,
    @location(1) normal: vec3<f32>,
    @location(2) tex_coord: vec2<f32>,
    @location(3) joints: vec4<u32>,
    @location(4) weights: vec4<f32>,
};

struct VertexPayload {
    @builtin(position) position: vec4<f32>,
    @location(0) tex_coord: vec2<f32>,
    @location(1) normal: vec3<f32>,
};

@vertex
fn vs_main(vertex: Vertex) -> VertexPayload {

    var out: VertexPayload;
    out.position = view_projection * model * vec4<f32>(vertex.position, 1.0);
    out.tex_coord = vertex.tex_coord;
    out.normal = normalize((model * vec4<f32>(vertex.normal, 0.0)).xyz);
    return out;
}

@fragment
fn fs_main(in: VertexPayload) -> @location(0) vec4<f32> {
    var sun_direction: vec3<f32> = normalize(vec3<f32>(1.0, -1.0, 1.0));
    var light_strength: f32 = max(0.0, dot(in.normal, sun_direction));
    var base: vec4<f32> = textureSample(myTexture, mySampler, in.tex_coord);
    return vec4<f32>(light_strength * base.rgb, base.a);
}