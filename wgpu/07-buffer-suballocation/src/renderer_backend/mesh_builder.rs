use glm::*;
use wgpu::util::DeviceExt;

pub struct Mesh {
    pub buffer: wgpu::Buffer,
    pub offset: u64,
}

#[repr(C)] // C-style data layout
pub struct Vertex {
    position: Vec3,
    color: Vec3
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

// From: https://stackoverflow.com/questions/28127165/how-to-convert-struct-to-u8
unsafe fn any_as_u8_slice<T: Sized>(p: &T) -> &[u8] {
    ::core::slice::from_raw_parts(
        (p as *const T) as *const u8,
        ::core::mem::size_of::<T>(),
    )
}

pub fn make_triangle(device: &wgpu::Device) -> wgpu::Buffer {
    
    let vertices: [Vertex; 3] = [
        Vertex {position: Vec3::new(-0.75, -0.75, 0.0), color: Vec3::new(1.0, 0.0, 0.0)},
        Vertex {position: Vec3::new( 0.75, -0.75, 0.0), color: Vec3::new(0.0, 1.0, 0.0)},
        Vertex {position: Vec3::new(  0.0,  0.75, 0.0), color: Vec3::new(0.0, 0.0, 1.0)}
    ];
    let bytes: &[u8] = unsafe { any_as_u8_slice(&vertices) };

    let buffer_descriptor = wgpu::util::BufferInitDescriptor { 
        label: Some("Triangle vertex buffer"), 
        contents: bytes,
         usage: wgpu::BufferUsages::VERTEX };

    let vertex_buffer = device.create_buffer_init(&buffer_descriptor);

    return vertex_buffer;
    
}

pub fn make_quad(device: &wgpu::Device) -> Mesh {
    
    let vertices: [Vertex; 4] = [
        Vertex {position: Vec3::new(-0.75, -0.75, 0.0), color: Vec3::new(1.0, 0.0, 0.0)},
        Vertex {position: Vec3::new( 0.75, -0.75, 0.0), color: Vec3::new(0.0, 1.0, 0.0)},
        Vertex {position: Vec3::new( 0.75,  0.75, 0.0), color: Vec3::new(0.0, 0.0, 1.0)},
        Vertex {position: Vec3::new(-0.75,  0.75, 0.0), color: Vec3::new(0.0, 1.0, 1.0)}
    ];
    let indices: [u16; 6] = [0, 1, 2, 2, 3, 0];

    let bytes_1: &[u8] = unsafe { any_as_u8_slice(&vertices) };
    let bytes_2: &[u8] = unsafe { any_as_u8_slice(&indices) };
    let bytes_merged: &[u8] = &[bytes_1, bytes_2].concat();

    let buffer_descriptor = wgpu::util::BufferInitDescriptor { 
        label: Some("Quad vertex & index buffer"), 
        contents: bytes_merged,
        usage: wgpu::BufferUsages::VERTEX | wgpu::BufferUsages::INDEX };

    let buffer = device.create_buffer_init(&buffer_descriptor);
    let offset: u64 = bytes_1.len().try_into().unwrap();

    Mesh { buffer, offset }
    
}