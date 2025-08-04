pub struct Builder<'a> {
    entries: Vec<wgpu::BindGroupLayoutEntry>,
    device: &'a wgpu::Device,
}

impl<'a> Builder<'a> {

    pub fn new(device: &'a wgpu::Device) -> Self {

        Builder {
            entries: Vec::new(),
            device: device,
        }
    }

    fn reset(&mut self) {
        self.entries.clear();
    }

    pub fn add_texture(&mut self) {

        self.entries.push(wgpu::BindGroupLayoutEntry {
            binding: self.entries.len() as u32,
            visibility: wgpu::ShaderStages::FRAGMENT,
            ty: wgpu::BindingType::Texture {
                multisampled: false,
                view_dimension: wgpu::TextureViewDimension::D2,
                sample_type: wgpu::TextureSampleType::Float { filterable: true },
            },
            count: None,});
        
        self.entries.push(wgpu::BindGroupLayoutEntry {
            binding: self.entries.len() as u32,
            visibility: wgpu::ShaderStages::FRAGMENT,
            ty: wgpu::BindingType::Sampler(wgpu::SamplerBindingType::Filtering),
            count: None,});
    }

    pub fn add_vec4(&mut self) {
        self.entries.push(wgpu::BindGroupLayoutEntry {
            binding: self.entries.len() as u32,
            visibility: wgpu::ShaderStages::FRAGMENT,
            ty: wgpu::BindingType::Buffer { 
                ty: wgpu::BufferBindingType::Uniform, 
                has_dynamic_offset: false, 
                min_binding_size: None },
            count: None
        });
    }

    pub fn add_mat4(&mut self) {
        self.entries.push(wgpu::BindGroupLayoutEntry {
            binding: self.entries.len() as u32,
            visibility: wgpu::ShaderStages::VERTEX,
            ty: wgpu::BindingType::Buffer { 
                ty: wgpu::BufferBindingType::Uniform, 
                has_dynamic_offset: false, 
                min_binding_size: None },
            count: None
        });
    }

    pub fn build(&mut self, label: &str) -> wgpu::BindGroupLayout {

        let layout = self.device.create_bind_group_layout(
            &wgpu::BindGroupLayoutDescriptor {
            entries: &self.entries,
            label: Some(label)});

        self.reset();

        layout
    }
}