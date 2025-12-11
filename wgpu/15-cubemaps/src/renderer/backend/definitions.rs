use glm::*;

#[derive(Eq, Hash, PartialEq)]
pub enum BindScope {
    Texture,
    Color,
    UBO,
    Skybox
}

#[derive(Eq, Hash, PartialEq, Clone, Copy)]
pub enum PipelineType {
    Simple,
    TexturedModel,
    ColoredModel,
    SkeletalModel,
    Skybox
}

pub struct Material {
    pub pipeline_type: PipelineType,
    pub color: Option<Vec4>,
    pub filename: Option<String>,
    pub bind_group: Option<wgpu::BindGroup>,
}

impl Material {
    pub fn new() -> Self {
        Material { 
            pipeline_type: PipelineType::Simple, 
            color: None,
            filename: None,
            bind_group: None }
    }
}

#[derive(Clone, Copy)]
pub struct Submesh {
    pub first_index: i32,
    pub index_count: u32,
    pub material_id: usize,
}

pub struct Model {
    pub buffer: wgpu::Buffer,
    pub ebo_offset: u64,
    pub submeshes: Vec<Submesh>,
}

pub struct SkeletalModel {
    pub index_count: u32,
    pub buffer: Option<wgpu::Buffer>,
    pub ebo_offset: u64,
    pub material_filename: Option<String>,
    pub material: Option<wgpu::BindGroup>,
}

#[repr(C)] // C-style data layout
pub struct Vertex {
    pub position: Vec3,
    pub color: Vec3
}

impl Vertex {

    pub fn get_layout() -> wgpu::VertexBufferLayout<'static> {

        const ATTRIBUTES: [wgpu::VertexAttribute; 2] = wgpu::vertex_attr_array![0 => Float32x3, 1 => Float32x3];

        wgpu::VertexBufferLayout {
            array_stride: std::mem::size_of::<Vertex>() as wgpu::BufferAddress,
            step_mode: wgpu::VertexStepMode::Vertex,
            attributes: &ATTRIBUTES
        }
    }
}

#[repr(C)] // C-style data layout
pub struct ModelVertex {
    pub position: Vec3,
    pub tex_coord: Vec2,
    pub normal: Vec3
}

impl ModelVertex {

    pub fn get_layout() -> wgpu::VertexBufferLayout<'static> {

        const ATTRIBUTES: [wgpu::VertexAttribute; 3] = wgpu::vertex_attr_array![
            0 => Float32x3,
            1 => Float32x2,
            2 => Float32x3];

        wgpu::VertexBufferLayout {
            array_stride: std::mem::size_of::<ModelVertex>() as wgpu::BufferAddress,
            step_mode: wgpu::VertexStepMode::Vertex,
            attributes: &ATTRIBUTES
        }
    }
}

#[repr(C)] // C-style data layout
pub struct SkeletalVertex {
    pub position: Vec3,
    pub normal: Vec3,
    pub tex_coord: Vec2,
    pub joints: [u8; 4],
    pub weights: Vec4,
}

impl SkeletalVertex {

    pub fn get_layout() -> wgpu::VertexBufferLayout<'static> {

        const ATTRIBUTES: [wgpu::VertexAttribute; 5] = wgpu::vertex_attr_array![
            0 => Float32x3,
            1 => Float32x3,
            2 => Float32x2,
            3 => Uint8x4,
            4 => Float32x4];

        wgpu::VertexBufferLayout {
            array_stride: std::mem::size_of::<SkeletalVertex>() as wgpu::BufferAddress,
            step_mode: wgpu::VertexStepMode::Vertex,
            attributes: &ATTRIBUTES
        }
    }
}