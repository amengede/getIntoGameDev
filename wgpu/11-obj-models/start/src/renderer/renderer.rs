use glfw::Window;
use crate::renderer::backend::{
    bind_group_layout, material::Material, mesh_builder, pipeline, 
    ubo::{UBO, UBOGroup}};
use crate::model::game_objects::{Camera, Object};
use glm::{ext, dot, radians};

pub struct State<'a> {
    instance: wgpu::Instance,
    surface: wgpu::Surface<'a>,
    device: wgpu::Device,
    queue: wgpu::Queue,
    config: wgpu::SurfaceConfiguration,
    pub size: (i32, i32),
    pub window: &'a mut Window,
    render_pipeline: wgpu::RenderPipeline,
    triangle_mesh: wgpu::Buffer,
    quad_mesh: mesh_builder::Mesh,
    triangle_material: Material,
    quad_material: Material,
    ubo: Option<UBOGroup>,
    projection_ubo: UBO,
}

impl<'a> State<'a> {

    pub async fn new(window: &'a mut Window) -> Self {

        let size = window.get_framebuffer_size();

        let instance_descriptor = wgpu::InstanceDescriptor {
            backends: wgpu::Backends::all(), ..Default::default()
        };
        let instance = wgpu::Instance::new(&instance_descriptor);
        let surface = instance.create_surface(window.render_context()).unwrap();

        let adapter_descriptor = wgpu::RequestAdapterOptionsBase {
            power_preference: wgpu::PowerPreference::default(),
            compatible_surface: Some(&surface),
            force_fallback_adapter: false,
        };
        let adapter = instance.request_adapter(&adapter_descriptor)
            .await.unwrap();

        let device_descriptor = wgpu::DeviceDescriptor {
            required_features: wgpu::Features::empty(),
            required_limits: wgpu::Limits::default(),
            memory_hints: wgpu::MemoryHints::Performance,
            label: Some("Device"),
            trace: wgpu::Trace::Off,
            experimental_features: wgpu::ExperimentalFeatures::disabled()
        };
        let (device, queue) = adapter
            .request_device(&device_descriptor)
            .await.unwrap();


        let surface_capabilities = surface.get_capabilities(&adapter);
        let surface_format = surface_capabilities
            .formats
            .iter()
            .copied()
            .filter(|f | f.is_srgb())
            .next()
            .unwrap_or(surface_capabilities.formats[0]);
        let config = wgpu::SurfaceConfiguration {
            usage: wgpu::TextureUsages::RENDER_ATTACHMENT,
            format: surface_format,
            width: size.0 as u32,
            height: size.1 as u32,
            present_mode: surface_capabilities.present_modes[0],
            alpha_mode: surface_capabilities.alpha_modes[0],
            view_formats: vec![],
            desired_maximum_frame_latency: 2
        };
        surface.configure(&device, &config);

        let triangle_buffer = mesh_builder::make_triangle(&device);

        let quad_mesh = mesh_builder::make_quad(&device);

        let material_bind_group_layout;
        {
            let mut builder = bind_group_layout::Builder::new(&device);
            builder.add_material();
            material_bind_group_layout = builder.build("Material Bind Group Layout");
        }

        let ubo_bind_group_layout;
        {
            let mut builder = bind_group_layout::Builder::new(&device);
            builder.add_ubo();
            ubo_bind_group_layout = builder.build("UBO Bind Group Layout");
        }

        let render_pipeline: wgpu::RenderPipeline;
        {
            let mut builder = pipeline::Builder::new(&device);
            builder.set_shader_module("shaders/shader.wgsl", "vs_main", "fs_main");
            builder.set_pixel_format(config.format);
            builder.add_vertex_buffer_layout(mesh_builder::Vertex::get_layout());
            builder.add_bind_group_layout(&material_bind_group_layout);
            builder.add_bind_group_layout(&ubo_bind_group_layout);
            builder.add_bind_group_layout(&ubo_bind_group_layout);
            render_pipeline = builder.build("Render Pipeline");
        }

        let triangle_material = Material::new("../img/winry.jpg", &device, &queue, "Triangle Material", &material_bind_group_layout);
        let quad_material = Material::new("../img/satin.jpg", &device, &queue, "Quad Material", &material_bind_group_layout);

        let projection_ubo = UBO::new(&device, ubo_bind_group_layout);

        Self {
            instance,
            window,
            surface,
            device,
            queue,
            config,
            size,
            render_pipeline,
            triangle_mesh: triangle_buffer,
            quad_mesh,
            triangle_material: triangle_material,
            quad_material: quad_material,
            ubo: None,
            projection_ubo: projection_ubo
        }
    }

    pub fn resize(&mut self, new_size: (i32, i32)) {
        if new_size.0 > 0 && new_size.1 > 0 {
            self.size = new_size;
            self.config.width = new_size.0 as u32;
            self.config.height = new_size.1 as u32;
            self.surface.configure(&self.device, &self.config);
        }
    }

    pub fn update_surface(&mut self) {
        self.surface = self.instance.create_surface(self.window.render_context()).unwrap();
    }

    pub fn build_ubos_for_objects(&mut self, object_count: usize) {

        let ubo_bind_group_layout;
        {
            let mut builder = bind_group_layout::Builder::new(&self.device);
            builder.add_ubo();
            ubo_bind_group_layout = builder.build("UBO Bind Group Layout");
        }
        self.ubo = Some(UBOGroup::new(&self.device, object_count, ubo_bind_group_layout));
    }

    fn update_projection(&mut self, camera: &Camera) {

        let c0 = glm::Vec4::new(camera.right.x, camera.up.x, -camera.forwards.x, 0.0);
        let c1 = glm::Vec4::new(camera.right.y, camera.up.y, -camera.forwards.y, 0.0);
        let c2 = glm::Vec4::new(camera.right.z, camera.up.z, -camera.forwards.z, 0.0);
        let a: f32 = -dot(camera.right, camera.position);
        let b: f32 = -dot(camera.up, camera.position);
        let c: f32 = dot(camera.forwards, camera.position);
        let c3 = glm::Vec4::new(a, b, c, 1.0);
        let view = glm::Matrix4::new(c0, c1, c2, c3);

        let fov_y: f32 = radians(45.0);
        let aspect = 4.0 / 3.0;
        let z_near = 0.1;
        let z_far = 10.0;
        let projection = ext::perspective(fov_y, aspect, z_near, z_far);
        
        let view_proj = projection * view;
        self.projection_ubo.upload(&view_proj, &self.queue);
    }

    fn update_transforms(&mut self, quads: &Vec<Object>, tris: &Vec<Object>) {
        let mut offset: u64 = 0;
        for i in 0..quads.len() {
            let c0 = glm::Vec4::new(1.0, 0.0, 0.0, 0.0);
            let c1 = glm::Vec4::new(0.0, 1.0, 0.0, 0.0);
            let c2 = glm::Vec4::new(0.0, 0.0, 1.0, 0.0);
            let c3 = glm::Vec4::new(0.0, 0.0, 0.0, 1.0);
            let m1 = glm::Matrix4::new(c0, c1, c2, c3);
            let m2 = glm::Matrix4::new(c0, c1, c2, c3);
            let matrix = 
                ext::rotate(&m2, quads[i].angle, glm::Vector3::new(0.0, 0.0, 1.0)) 
                * ext::translate(&m1, quads[i].position);
            self.ubo.as_mut().unwrap().upload(offset + i as u64, &matrix, &self.queue);
        }

        offset = quads.len() as u64;
        for i in 0..tris.len() {
            let c0 = glm::Vec4::new(1.0, 0.0, 0.0, 0.0);
            let c1 = glm::Vec4::new(0.0, 1.0, 0.0, 0.0);
            let c2 = glm::Vec4::new(0.0, 0.0, 1.0, 0.0);
            let c3 = glm::Vec4::new(0.0, 0.0, 0.0, 1.0);
            let m1 = glm::Matrix4::new(c0, c1, c2, c3);
            let m2 = glm::Matrix4::new(c0, c1, c2, c3);
            let matrix = 
                ext::rotate(&m2, tris[i].angle, glm::Vector3::new(0.0, 0.0, 1.0)) 
                * ext::translate(&m1, tris[i].position);
            self.ubo.as_mut().unwrap().upload(offset + i as u64, &matrix, &self.queue);
        }
    }

    pub fn render(&mut self, quads: &Vec<Object>, 
        tris: &Vec<Object>,
        camera: &Camera) -> Result<(), wgpu::SurfaceError>{

        self.device.poll(wgpu::PollType::Wait{submission_index: None, timeout: None}).ok();

        // Upload
        self.update_projection(camera);
        self.update_transforms(quads, tris);

        let event = self.queue.submit([]);
        let maintain = wgpu::PollType::Wait{
            submission_index: Some(event), timeout: None };
        self.device.poll(maintain).ok();

        let drawable = self.surface.get_current_texture()?;
        let image_view_descriptor = wgpu::TextureViewDescriptor::default();
        let image_view = drawable.texture.create_view(&image_view_descriptor);

        let command_encoder_descriptor = wgpu::CommandEncoderDescriptor {
            label: Some("Render Encoder")
        };
        let mut command_encoder = self.device.create_command_encoder(&command_encoder_descriptor);

        let color_attachment = wgpu::RenderPassColorAttachment {
            view: &image_view,
            resolve_target: None,
            ops: wgpu::Operations {
                load: wgpu::LoadOp::Clear(wgpu::Color {
                    r: 0.75,
                    g: 0.5,
                    b: 0.25,
                    a: 1.0
                }),
                store: wgpu::StoreOp::Store,
            },
            depth_slice: None
        };

        let render_pass_descriptor = wgpu::RenderPassDescriptor {
            label: Some("Render Pass"),
            color_attachments: &[Some(color_attachment)],
            depth_stencil_attachment: None,
            occlusion_query_set: None,
            timestamp_writes: None
        };

        {
            let mut renderpass = command_encoder.begin_render_pass(&render_pass_descriptor);
            renderpass.set_pipeline(&self.render_pipeline);

            // Quads
            renderpass.set_bind_group(0, &self.quad_material.bind_group, &[]);
            renderpass.set_bind_group(2, &self.projection_ubo.bind_group, &[]);
            renderpass.set_vertex_buffer(0, 
                self.quad_mesh.buffer.slice(0..self.quad_mesh.offset));
            renderpass.set_index_buffer(self.quad_mesh.buffer.slice(self.quad_mesh.offset..), 
                wgpu::IndexFormat::Uint16);
            let mut offset: usize = 0;
            for i in 0..quads.len() {
                renderpass.set_bind_group(
                    1, 
                    &(self.ubo.as_ref().unwrap()).bind_groups[offset + i], 
                    &[]);
                renderpass.draw_indexed(0..6, 0, 0..1);
            }

            // Triangles
            renderpass.set_bind_group(0, &self.triangle_material.bind_group, &[]);
            renderpass.set_vertex_buffer(0, self.triangle_mesh.slice(..));
            offset = quads.len();
            for i in 0..tris.len() {
                renderpass.set_bind_group(
                    1, 
                    &(self.ubo.as_ref().unwrap()).bind_groups[offset + i], 
                    &[]);
                renderpass.draw(0..3, 0..1);
            }
        }
        self.queue.submit(std::iter::once(command_encoder.finish()));
        self.device.poll(wgpu::PollType::Wait {submission_index: None, timeout: None}).ok();

        drawable.present();

        Ok(())
    }
}
