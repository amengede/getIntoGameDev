pub struct Builder<'a> {
    entries: Vec<wgpu::BindGroupEntry<'a>>,
    layout: Option<&'a wgpu::BindGroupLayout>,
    device: &'a wgpu::Device,
}

impl<'a> Builder<'a> {

    pub fn new(device: &'a wgpu::Device) -> Self {

        Builder {
            entries: Vec::new(),
            layout: None,
            device: device,
        }
    }

    fn reset(&mut self) {
        self.entries.clear();
    }

    pub fn set_layout(&mut self, layout: &'a wgpu::BindGroupLayout) {
        self.layout = Some(layout);
    }

    pub fn add_material(&mut self, view: &'a wgpu::TextureView, sampler: &'a wgpu::Sampler) {

        self.entries.push(wgpu::BindGroupEntry {
            binding: self.entries.len() as u32,
            resource: wgpu::BindingResource::TextureView(view),
        });
        
        self.entries.push(wgpu::BindGroupEntry {
            binding: self.entries.len() as u32,
            resource: wgpu::BindingResource::Sampler(sampler),
        });
    }

    pub fn build(&mut self, label: &str) -> wgpu::BindGroup {

        let bind_group = self.device.create_bind_group(
        &wgpu::BindGroupDescriptor {
            layout: self.layout.unwrap(),
            entries: &self.entries,
            label: Some(label),
        });

        self.reset();

        bind_group
    }
}
