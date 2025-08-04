use std::env::current_dir;
use std::fs;

pub struct Builder<'a> {
    shader_filename: String,
    vertex_entry: String,
    fragment_entry: String,
    pixel_format: wgpu::TextureFormat,
    vertex_buffer_layouts: Vec<wgpu::VertexBufferLayout<'static>>,
    bind_group_layouts: Vec<&'a wgpu::BindGroupLayout>,
    device: &'a wgpu::Device,
}

impl<'a> Builder<'a> {
    
    pub fn new(device: &'a wgpu::Device) -> Self {
        Builder {
            shader_filename: "dummy".to_string(),
            vertex_entry: "dummy".to_string(),
            fragment_entry: "dummy".to_string(),
            pixel_format: wgpu::TextureFormat::Rgba8Unorm,
            vertex_buffer_layouts: Vec::new(),
            bind_group_layouts: Vec::new(),
            device: device,
        }
    }

    fn reset(&mut self) {
        self.vertex_buffer_layouts.clear();
        self.bind_group_layouts.clear();
    }

    pub fn add_vertex_buffer_layout(&mut self, layout: wgpu::VertexBufferLayout<'static>) {
        self.vertex_buffer_layouts.push(layout);
    }

    pub fn add_bind_group_layout(&mut self, layout: &'a wgpu::BindGroupLayout) {
        self.bind_group_layouts.push(layout);
    }

    pub fn set_shader_module(&mut self, shader_filename: &str, vertex_entry: &str, fragment_entry: &str) {

        self.shader_filename = shader_filename.to_string();
        self.vertex_entry = vertex_entry.to_string();
        self.fragment_entry = fragment_entry.to_string();
    }

    pub fn set_pixel_format(&mut self, pixel_format: wgpu::TextureFormat) {

        self.pixel_format = pixel_format;
    }

    pub fn build(&mut self, label: &str) -> wgpu::RenderPipeline {

        let mut filepath = current_dir().unwrap();
        filepath.push("src/");
        filepath.push(self.shader_filename.as_str());
        let filepath = filepath.into_os_string().into_string().unwrap();
        let source_code = fs::read_to_string(filepath).expect("Can't read source code!");

        let shader_module_descriptor = wgpu::ShaderModuleDescriptor {
            label: Some("Shader Module"),
            source: wgpu::ShaderSource::Wgsl(source_code.into()),
        };
        let shader_module = self.device.create_shader_module(shader_module_descriptor);

        let pipeline_layout_descriptor = wgpu::PipelineLayoutDescriptor {
            label: Some("Render Pipeline Layout"),
            bind_group_layouts: &self.bind_group_layouts,
            push_constant_ranges: &[],
        };
        let pipeline_layout: wgpu::PipelineLayout = self.device.create_pipeline_layout(&pipeline_layout_descriptor);

        let render_targets = [Some(wgpu::ColorTargetState {
            format: self.pixel_format,
            blend: Some(wgpu::BlendState::REPLACE),
            write_mask: wgpu::ColorWrites::ALL,
        })];

        let render_pipeline_descriptor = wgpu::RenderPipelineDescriptor {
            label: Some(label),
            layout: Some(&pipeline_layout),

            vertex: wgpu::VertexState {
                module: &shader_module,
                entry_point: &self.vertex_entry,
                buffers: &self.vertex_buffer_layouts,
            },

            primitive: wgpu::PrimitiveState {
                topology: wgpu::PrimitiveTopology::TriangleList,
                strip_index_format: None,
                front_face: wgpu::FrontFace::Ccw,
                cull_mode: Some(wgpu::Face::Back),
                polygon_mode: wgpu::PolygonMode::Fill,
                unclipped_depth: false,
                conservative: false,
            },

            fragment: Some(wgpu::FragmentState {
                module: &shader_module,
                entry_point: &self.fragment_entry,
                targets: &render_targets,
            }),

            depth_stencil: None,
            multisample: wgpu::MultisampleState {
                count: 1,
                mask: !0,
                alpha_to_coverage_enabled: false,
            },
            multiview: None
        };

        let pipeline = self.device.create_render_pipeline(&render_pipeline_descriptor);

        self.reset();

        pipeline
    }
}