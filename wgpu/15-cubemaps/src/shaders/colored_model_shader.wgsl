struct Camera {
    pos: vec3<f32>,
    forwards: vec3<f32>,
    right: vec3<f32>,
    up: vec3<f32> 
}

@group(0) @binding(0) var<uniform> color: vec4<f32>;
@group(1) @binding(0) var<uniform> model: mat4x4<f32>;
@group(2) @binding(0) var<uniform> view_projection: mat4x4<f32>;
@group(3) @binding(0) var<uniform> camera: Camera;
@group(3) @binding(1) var skyTexture: texture_cube<f32>;
@group(3) @binding(2) var skySampler: sampler;

struct Vertex {
    @location(0) position: vec3<f32>,
    @location(1) tex_coord: vec2<f32>,
    @location(2) normal: vec3<f32>,
};

struct VertexPayload {
    @builtin(position) position: vec4<f32>,
    @location(0) normal: vec3<f32>,
    @location(1) outgoing: vec3<f32>
};

@vertex
fn vs_main(vertex: Vertex) -> VertexPayload {

    var out: VertexPayload;
    var world_pos: vec3<f32> = (model * vec4<f32>(vertex.position, 1.0)).xyz;
    out.position = view_projection * vec4<f32>(world_pos, 1.0);
    out.normal = (model * vec4<f32>(vertex.normal, 0.0)).xyz;

    var incident: vec3<f32> = normalize(world_pos - camera.pos);
    out.outgoing = reflect(incident, out.normal);
    return out;
}

@fragment
fn fs_main(in: VertexPayload) -> @location(0) vec4<f32> {
    var sun_direction: vec3<f32> = normalize(vec3<f32>(1.0, 1.0, -1.0));
    var light_strength: f32 = max(0.0, dot(in.normal, sun_direction));

    var reflection: vec4<f32> = textureSample(skyTexture, skySampler, in.outgoing);
    return vec4<f32>(light_strength * color.rgb * reflection.rgb, 1.0);
}