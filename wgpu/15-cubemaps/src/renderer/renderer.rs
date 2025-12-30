use glfw::Window;
use crate::model::character::Character;
use crate::renderer::backend::bind_group;
use crate::renderer::backend::texture::new_cubemap;
use crate::renderer::backend::{
    bind_group_layout,
    definitions::{SkeletalModel, SkeletalVertex},
    mesh_builder::{self, ObjLoader}, pipeline,
    texture::{new_color, new_depth_texture, new_texture, Texture},
    ubo::{UBOGroup, UBO}};
use crate::model::game_objects::{Camera, Object};
use glm::{ext, dot, radians};
use crate::renderer::backend::definitions::{Vertex, Model};
use std::collections::HashMap;
use crate::utility::math::{from_translation, x_axis_rotation, y_axis_rotation, z_axis_rotation};

use super::backend::definitions::{ModelVertex, BindScope, PipelineType, Material};
use crate::model::common::ObjectType;
use super::backend::mesh_builder::any_as_u8_slice;

struct DrawCommand {
    object_type: ObjectType,
    object_index: usize
}

struct SkeletalDrawCommand {
    object_type: ObjectType,
    object_index: usize,
    skeleton_index: usize
}

pub struct State<'a> {
    instance: wgpu::Instance,
    surface: wgpu::Surface<'a>,
    device: wgpu::Device,
    queue: wgpu::Queue,
    config: wgpu::SurfaceConfiguration,
    pub size: (i32, i32),
    pub window: &'a mut Window,
    render_pipelines: HashMap<PipelineType, wgpu::RenderPipeline>,
    ubo: Option<UBOGroup>,
    bone_ubos: Vec<UBO>,
    projection_ubo: UBO,
    bind_group_layouts: HashMap<BindScope, wgpu::BindGroupLayout>,
    models: HashMap<ObjectType, Model>,
    skeletal_models: HashMap<ObjectType, SkeletalModel>,
    materials: Vec<Material>,
    depth_buffer: Texture,
    static_draw_commands: Vec<DrawCommand>,
    animated_draw_commands: Vec<SkeletalDrawCommand>,
    camera_buffer: wgpu::Buffer,
    skybox: Option<wgpu::BindGroup>
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

        let mut limits = wgpu::Limits::default();
        limits.max_bind_groups = 8;
        let device_descriptor = wgpu::DeviceDescriptor {
            required_features: wgpu::Features::empty(),
            required_limits: limits,
            memory_hints: wgpu::MemoryHints::Performance,
            label: Some("Device"),
            trace: wgpu::Trace::Off,
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

        let bind_group_layouts = 
            Self::build_bind_group_layouts(&device);

        let render_pipelines = 
            Self::build_pipelines(&device, &config, &bind_group_layouts);

        let projection_ubo = UBO::new(
            &device, 
            &bind_group_layouts[&BindScope::UBO],
            std::mem::size_of::<glm::Mat4>() as u64,
            "Projection UBO"
        );

        let buffer_descriptor = wgpu::BufferDescriptor {
            label: Some("Camera buffer descriptor"),
            size: 64,
            usage: wgpu::BufferUsages::COPY_DST | wgpu::BufferUsages::UNIFORM,
            mapped_at_creation: false
        };
        let camera_buffer = device.create_buffer(&buffer_descriptor);
        let skybox = None;
        
        let depth_buffer = new_depth_texture(&device, &config, "Depth Buffer");

        Self {
            instance,
            window,
            surface,
            device,
            queue,
            config,
            size,
            render_pipelines,
            ubo: None,
            projection_ubo: projection_ubo,
            bind_group_layouts: bind_group_layouts,
            models: HashMap::new(),
            materials: Vec::new(),
            depth_buffer,
            skeletal_models: HashMap::new(),
            bone_ubos: Vec::new(),
            static_draw_commands: Vec::new(),
            animated_draw_commands: Vec::new(),
            camera_buffer,
            skybox
        }
    }

    fn build_bind_group_layouts(device: &wgpu::Device) 
        -> HashMap<BindScope, wgpu::BindGroupLayout> {
        let mut layouts: HashMap<BindScope, wgpu::BindGroupLayout> = HashMap::new();
        let mut layout: wgpu::BindGroupLayout;
        let mut scope = BindScope::Texture;
        let mut builder = bind_group_layout::Builder::new(device);
        builder.add_texture();
        layout = builder.build("Texture Bind Group Layout");
        layouts.insert(scope, layout);

        builder.add_ubo(wgpu::ShaderStages::FRAGMENT);
        scope = BindScope::Color;
        layout = builder.build("Color Group Layout");
        layouts.insert(scope, layout);
        
        builder.add_ubo(wgpu::ShaderStages::VERTEX);
        scope = BindScope::UBO;
        layout = builder.build("UBO Bind Group Layout");
        layouts.insert(scope, layout);

        builder.add_ubo(wgpu::ShaderStages::VERTEX);
        builder.add_cubemap();
        scope = BindScope::Skybox;
        layout = builder.build("Skybox Bind Group Layout");
        layouts.insert(scope, layout);

        layouts
    }

    fn build_pipelines(device: &wgpu::Device, 
        config: &wgpu::SurfaceConfiguration, 
        bind_group_layouts: &HashMap<BindScope, wgpu::BindGroupLayout>) 
        -> HashMap<PipelineType, wgpu::RenderPipeline> {
        
        let mut pipelines: HashMap<PipelineType, wgpu::RenderPipeline> = HashMap::new();
        let mut pipeline_type: PipelineType;
        let mut pipeline: wgpu::RenderPipeline;
        let mut builder = pipeline::Builder::new(device);
        pipeline_type = PipelineType::Simple;
        builder.set_shader_module("shaders/shader.wgsl", 
            "vs_main", "fs_main");
        builder.set_pixel_format(config.format);
        builder.add_vertex_buffer_layout(Vertex::get_layout());
        builder.add_bind_group_layout(&bind_group_layouts[&BindScope::Texture]);
        builder.add_bind_group_layout(&bind_group_layouts[&BindScope::UBO]);
        builder.add_bind_group_layout(&bind_group_layouts[&BindScope::UBO]);
        pipeline = builder.build("Simple Pipeline");
        pipelines.insert(pipeline_type, pipeline);

        pipeline_type = PipelineType::ColoredModel;
        builder.set_shader_module("shaders/colored_model_shader.wgsl", 
            "vs_main", "fs_main");
        builder.set_pixel_format(config.format);
        builder.add_vertex_buffer_layout(ModelVertex::get_layout());
        builder.add_bind_group_layout(&bind_group_layouts[&BindScope::Color]);
        builder.add_bind_group_layout(&bind_group_layouts[&BindScope::UBO]);
        builder.add_bind_group_layout(&bind_group_layouts[&BindScope::UBO]);
        builder.add_bind_group_layout(&bind_group_layouts[&BindScope::Skybox]); // skybox
        pipeline = builder.build("Colored Model Pipeline");
        pipelines.insert(pipeline_type, pipeline);

        pipeline_type = PipelineType::TexturedModel;
        builder.set_shader_module("shaders/textured_model_shader.wgsl", 
            "vs_main", "fs_main");
        builder.set_pixel_format(config.format);
        builder.add_vertex_buffer_layout(ModelVertex::get_layout());
        builder.add_bind_group_layout(&bind_group_layouts[&BindScope::Texture]);
        builder.add_bind_group_layout(&bind_group_layouts[&BindScope::UBO]);
        builder.add_bind_group_layout(&bind_group_layouts[&BindScope::UBO]);
        builder.add_bind_group_layout(&bind_group_layouts[&BindScope::Skybox]); // skybox
        pipeline = builder.build("Textured Model Pipeline");
        pipelines.insert(pipeline_type, pipeline);

        pipeline_type = PipelineType::SkeletalModel;
        builder.set_shader_module("shaders/skeletal_model_shader.wgsl", 
            "vs_main", "fs_main");
        builder.set_pixel_format(config.format);
        builder.add_vertex_buffer_layout(SkeletalVertex::get_layout());
        builder.add_bind_group_layout(&bind_group_layouts[&BindScope::Texture]);
        builder.add_bind_group_layout(&bind_group_layouts[&BindScope::UBO]); // model
        builder.add_bind_group_layout(&bind_group_layouts[&BindScope::UBO]); // viewProj
        builder.add_bind_group_layout(&bind_group_layouts[&BindScope::UBO]); // bone data
        builder.add_bind_group_layout(&bind_group_layouts[&BindScope::Skybox]); // skybox
        pipeline = builder.build("Skeletal Model Pipeline");
        pipelines.insert(pipeline_type, pipeline);

        pipeline_type = PipelineType::Skybox;
        builder.set_shader_module("shaders/sky_shader.wgsl", 
            "sky_vert_main", "sky_frag_main");
        builder.set_pixel_format(config.format);
        builder.add_bind_group_layout(&bind_group_layouts[&BindScope::Skybox]);
        pipeline = builder.build("Skybox Pipeline");
        pipelines.insert(pipeline_type, pipeline);

        pipelines
    }

    pub fn configure_window(&mut self) {
        self.window.set_framebuffer_size_polling(true);
        self.window.set_key_polling(true);
        self.window.set_mouse_button_polling(true);
        self.window.set_pos_polling(true);
        self.window.set_cursor_mode(glfw::CursorMode::Hidden);
    }

    pub fn load_assets(&mut self) {
        let mut loader = ObjLoader::new();

        let c0 = glm::Vec4::new(5.0, 0.0, 0.0, 0.0);
        let c1 = glm::Vec4::new(0.0, 5.0, 0.0, 0.0);
        let c2 = glm::Vec4::new(0.0, 0.0, 5.0, 0.0);
        let c3 = glm::Vec4::new(0.0, 0.0, 0.0, 1.0);
        let pre_transform = glm::Matrix4::new(c0, c1, c2, c3);

        self.models.insert(
            ObjectType::Poses, 
            loader.load("poses.obj",
                &mut self.materials,
                &self.device,
                &pre_transform));
        
        let c0 = glm::Vec4::new(0.05, 0.0, 0.0, 0.0);
        let c1 = glm::Vec4::new(0.0, 0.05, 0.0, 0.0);
        let c2 = glm::Vec4::new(0.0, 0.0, 0.05, 0.0);
        let c3 = glm::Vec4::new(0.0, 0.0, 0.0, 1.0);
        let translation = glm::Vec3::new(0.05, 0.05, 0.05);
        let pre_transform = from_translation(&translation)
                                            * z_axis_rotation(0.0)
                                            * y_axis_rotation(0.0)
                                            * x_axis_rotation(-90.0)
                                            * glm::Matrix4::new(c0, c1, c2, c3);

        self.models.insert(
            ObjectType::Gun,
            loader.load("gun.obj",
                &mut self.materials,
                &self.device,
                &pre_transform));

        for material in &mut self.materials {

            material.bind_group = match material.pipeline_type {

                PipelineType::ColoredModel => {
                    Some(new_color(
                        &(material.color.unwrap()), 
                        &self.device, 
                        "Color", 
                        &self.bind_group_layouts[&BindScope::Color]))

                }

                PipelineType::TexturedModel => {
                    Some(new_texture(
                        material.filename.as_ref().unwrap().as_str(), 
                        &self.device, 
                        &self.queue, "Texture", 
                        &self.bind_group_layouts[&BindScope::Texture]))
                }

                _ => {
                    None
                }
            }
        }

        let mut skeletal_model = mesh_builder::load_from_gltf(
            "modern_girl.gltf", &self.device);
        let filename = String::from(skeletal_model
                                                .material_filename
                                                .as_ref()
                                                .unwrap());
        let filename: String = "../img/".to_owned() + &filename + "_diffuse.png";
        skeletal_model.material = Some(new_texture(
            filename.as_str(), &self.device, &self.queue, 
            "Modern Girl diffuse", 
            &self.bind_group_layouts[&BindScope::Texture]));
        self.skeletal_models.insert(ObjectType::Girl, skeletal_model);

        let skybox_texture = new_cubemap(
            "sky2/sky", &self.device, &self.queue, "Skybox");
        {
            let mut builder = bind_group::Builder::new(&self.device);
            builder.set_layout(&self.bind_group_layouts[&BindScope::Skybox]);
            builder.add_buffer(&self.camera_buffer, 0);
            let sampler = skybox_texture.sampler.unwrap();
            builder.add_material(&skybox_texture.view, &sampler);
            self.skybox = Some(builder.build("Skybox bind group"));
        }
    }
    
    pub fn resize(&mut self, new_size: (i32, i32)) {
        if new_size.0 > 0 && new_size.1 > 0 {
            self.size = new_size;
            self.config.width = new_size.0 as u32;
            self.config.height = new_size.1 as u32;
            self.surface.configure(&self.device, &self.config);

            self.depth_buffer.texture.destroy();

            self.depth_buffer = new_depth_texture(&self.device, &self.config, "Depth Buffer");
        }
    }

    pub fn update_surface(&mut self) {
        self.surface = self.instance.create_surface(self.window.render_context()).unwrap();
    }

    pub fn build_ubos_for_objects(&mut self,
        object_count: usize,
        character_count: usize) {

        self.ubo = Some(UBOGroup::new(&self.device, object_count, 
            &self.bind_group_layouts[&BindScope::UBO]));
        
        self.bone_ubos.reserve(character_count);
        for _ in 0..character_count {
            self.bone_ubos.push(UBO::new(&self.device, 
            &self.bind_group_layouts[&BindScope::UBO], 
            128 * std::mem::size_of::<glm::Mat4>() as u64, "Bone UBO"));
        }
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
        let z_far = 100.0;
        let projection = ext::perspective(fov_y, aspect, z_near, z_far);
        
        let view_proj = projection * view;
        self.projection_ubo.upload(&view_proj, &self.queue);
    }

    fn record_draw_commands(&mut self, static_models: &Vec<Object>,
        animated_models: &Vec<Character>, camera: &Camera) {
        
        // reset drawing stuff
        self.static_draw_commands.clear();
        self.animated_draw_commands.clear();
        let mut object_offset: u64 = 0;
        let mut skeleton_offset: usize = 0;

        // static models
        for model in static_models {
            let matrix = z_axis_rotation(model.angle)
                * from_translation(&model.position);
            self.ubo.as_mut().unwrap().upload(object_offset, &matrix, &self.queue);
            self.static_draw_commands.push(DrawCommand {
                object_type: model.object_type,
                object_index: object_offset as usize });
            object_offset += 1;
        }

        // attachments
        for model in animated_models {
            let character_matrix = model.transform_component.get_transform();

            let skeleton = &model.skeleton_component;
            for attachment in &model.attachments {
                let socket_matrix = skeleton.sockets.get(attachment.0).unwrap().clone();
                let attachment_matrix = character_matrix * socket_matrix;
                self.ubo.as_mut().unwrap().upload(object_offset, &attachment_matrix, &self.queue);
                self.static_draw_commands.push(DrawCommand {
                    object_type: *attachment.1,
                    object_index: object_offset as usize });
                object_offset += 1;
            }
        }

        // animated models
        for model in animated_models {
            let character_matrix = model.transform_component.get_transform();
            self.ubo.as_mut().unwrap().upload(object_offset, &character_matrix, &self.queue);

            let skeleton = &model.skeleton_component;
            let matrices = &skeleton.transforms;
            self.bone_ubos[skeleton_offset].upload_vec(&matrices, &self.queue);
            

            self.animated_draw_commands.push(SkeletalDrawCommand {
                object_type: model.object_type,
                object_index: object_offset as usize,
                skeleton_index: skeleton_offset });
            object_offset += 1;
            skeleton_offset += 1;
        }

        // record camera data
        {
            let offset = 0;
            let pos = camera.position.extend(0.0);
            let forwards = camera.forwards.extend(0.0);
            let aspect: f32 = 3.0/4.0;
            let fov: f32 = glm::tan(glm::radians(45.0));
            let right = camera.right.extend(0.0) * fov;
            let up = camera.up.extend(0.0) * aspect * fov;

            let blob: &[u8] = &[
                unsafe { any_as_u8_slice(&pos) },
                unsafe { any_as_u8_slice(&forwards) },
                unsafe { any_as_u8_slice(&right) },
                unsafe { any_as_u8_slice(&up) }].concat();

            self.queue.write_buffer(&self.camera_buffer, offset, blob);
        }
    }

    fn render_model(& self, command: &DrawCommand, renderpass: &mut wgpu::RenderPass) {

        let model = self.models.get(&command.object_type).unwrap();

        // Bind vertex and index buffer
        renderpass.set_vertex_buffer(0, 
            model.buffer.slice(0..model.ebo_offset));
        renderpass.set_index_buffer(model.buffer.slice(model.ebo_offset..), 
            wgpu::IndexFormat::Uint32);
        
        // Transforms
        renderpass.set_bind_group(
            1, 
            &(self.ubo.as_ref().unwrap()).bind_groups[command.object_index], 
            &[]);
        
        for submesh in &model.submeshes {

            // Select pipeline
            let material = &self.materials[submesh.material_id];
            renderpass.set_pipeline(&self.render_pipelines[&material.pipeline_type]);
            renderpass.set_bind_group(0, 
                (material.bind_group).as_ref().unwrap(), &[]);
                
            renderpass.draw_indexed(0..submesh.index_count, submesh.first_index, 0..1);
        }
    }

    fn render_skeletal_model(& self, command: &SkeletalDrawCommand,
        renderpass: &mut wgpu::RenderPass) {

        let model = self.skeletal_models.get(&command.object_type).unwrap();
        // Bind vertex and index buffer
        renderpass.set_vertex_buffer(0, 
            model.buffer.as_ref().unwrap().slice(0..model.ebo_offset));
        renderpass.set_index_buffer(model.buffer.as_ref().unwrap().slice(model.ebo_offset..), 
            wgpu::IndexFormat::Uint16);
        
        // Transforms
        renderpass.set_bind_group(
            1, 
            &(self.ubo.as_ref().unwrap()).bind_groups[command.object_index], 
            &[]);
        renderpass.set_bind_group(3, &(self.bone_ubos[command.skeleton_index].bind_group), &[]);

        // Select pipeline
        let material = model.material.as_ref().unwrap();
        renderpass.set_bind_group(0, 
            material, &[]);
            
        renderpass.draw_indexed(0..model.index_count, 0, 0..1);
    }

    pub fn render(&mut self, static_models: &Vec<Object>,
        animated_models: &Vec<Character>,
        camera: &Camera) -> Result<(), wgpu::SurfaceError>{

        self.device.poll(wgpu::MaintainBase::Wait).ok();

        // Upload
        self.update_projection(camera);
        self.record_draw_commands(static_models, animated_models, camera);

        let event = self.queue.submit([]);
        let maintain = wgpu::MaintainBase::WaitForSubmissionIndex(event);
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
        };

        let depth_stencil_attachment = wgpu::RenderPassDepthStencilAttachment {
            view: &self.depth_buffer.view,
            depth_ops: Some(wgpu::Operations {
                load: wgpu::LoadOp::Clear(1.0),
                store: wgpu::StoreOp::Store,
            }),
            stencil_ops: None,
        };

        let render_pass_descriptor = wgpu::RenderPassDescriptor {
            label: Some("Render Pass"),
            color_attachments: &[Some(color_attachment)],
            depth_stencil_attachment: Some(depth_stencil_attachment),
            occlusion_query_set: None,
            timestamp_writes: None
        };

        {
            let mut renderpass = command_encoder.begin_render_pass(&render_pass_descriptor);
            renderpass.set_pipeline(&self.render_pipelines[&PipelineType::Simple]);

            renderpass.set_bind_group(2, &self.projection_ubo.bind_group, &[]);
            renderpass.set_bind_group(3, &self.skybox, &[]);
            for command in &self.static_draw_commands {
                self.render_model(command, &mut renderpass);
            }

            renderpass.set_pipeline(&self.render_pipelines[&PipelineType::SkeletalModel]);
            renderpass.set_bind_group(4, &self.skybox, &[]);
            for command in &self.animated_draw_commands {
                self.render_skeletal_model(command, &mut renderpass);
            }

            renderpass.set_pipeline(&self.render_pipelines[&PipelineType::Skybox]);
            renderpass.set_bind_group(0, &self.skybox, &[]);
            renderpass.draw(0..6, 0..1);
        }
        self.queue.submit(std::iter::once(command_encoder.finish()));
        self.device.poll(wgpu::MaintainBase::wait()).ok();

        drawable.present();

        Ok(())
    }
}
