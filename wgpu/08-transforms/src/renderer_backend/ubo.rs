use super::bind_group;
use super::mesh_builder::any_as_u8_slice;

pub struct UBO {
    pub buffer: wgpu::Buffer,
    pub bind_groups: Vec<wgpu::BindGroup>,
    allignment: u64,
}

impl UBO {

    pub fn new(device: &wgpu::Device, object_count: usize, layout: wgpu::BindGroupLayout) -> Self {

        let allignment = glm::max(
            device.limits().min_storage_buffer_offset_alignment as u32, 
            std::mem::size_of::<glm::Mat4>() as u32) as u64;

        let buffer_descriptor = wgpu::BufferDescriptor {
            label: Some("UBO"),
            size: object_count as u64 * allignment,
            usage: wgpu::BufferUsages::UNIFORM | wgpu::BufferUsages::COPY_DST,
            mapped_at_creation: false,
        };
        let buffer = device.create_buffer(&buffer_descriptor);

        // build bind groups
        let mut bind_groups: Vec<wgpu::BindGroup> = Vec::new();
        for i in 0..object_count {
            let mut builder = bind_group::Builder::new(device);
            builder.set_layout(&layout);
            builder.add_buffer(&buffer, i as u64 * allignment);
            bind_groups.push(builder.build("Matrix"));
        }

        Self { buffer, bind_groups, allignment }
    }

    pub fn upload(&mut self, i: u64, matrix: &glm::Mat4, queue: &wgpu::Queue) {
        let offset = i * self.allignment;
        let data: &[u8] = unsafe { any_as_u8_slice(matrix) };
        queue.write_buffer(&self.buffer, offset, data);
        
    }
}