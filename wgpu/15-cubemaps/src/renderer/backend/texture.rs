use crate::{renderer::backend::mesh_builder::any_as_u8_slice};
use wgpu::util::DeviceExt;
use crate::utility::file::read_to_byte_vec;
use image::GenericImageView;

use glm::Vec4;

use super::bind_group;

pub struct Texture {
    pub texture: wgpu::Texture,
    pub view: wgpu::TextureView,
    pub sampler: Option<wgpu::Sampler>,
}
    
pub fn new_depth_texture(device: &wgpu::Device, 
    config: &wgpu::SurfaceConfiguration, label: &str) -> Texture {

    let size = wgpu::Extent3d {
        width: config.width.max(1),
        height: config.height.max(1),
        depth_or_array_layers: 1,
    };

    let descriptor = wgpu::TextureDescriptor {
        label: Some(label),
        size,
        mip_level_count: 1,
        sample_count: 1,
        dimension: wgpu::TextureDimension::D2,
        format: wgpu::TextureFormat::Depth32Float,
        usage: wgpu::TextureUsages::RENDER_ATTACHMENT,
        view_formats: &[],
    };
    let texture = device.create_texture(&descriptor);

    let view = texture.create_view(&wgpu::TextureViewDescriptor::default());

    let sampler = None;

    Texture { texture, view, sampler }
}

pub fn new_texture(filename: &str, device: &wgpu::Device, 
    queue: &wgpu::Queue, label: &str, 
    layout: &wgpu::BindGroupLayout) -> wgpu::BindGroup {

    let bytes = read_to_byte_vec("src/", filename);
    let loaded_image = image::load_from_memory(&bytes).unwrap();
    let converted = loaded_image.to_rgba8();
    use image::GenericImageView;
    let size = loaded_image.dimensions();
    let texture_size = wgpu::Extent3d {
        width: size.0,
        height: size.1,
        depth_or_array_layers: 1};
    
    // Create the texture
    let texture_descriptor = wgpu::TextureDescriptor {
        size: texture_size,
        mip_level_count: 1,
        sample_count: 1,
        dimension: wgpu::TextureDimension::D2,
        format: wgpu::TextureFormat::Rgba8Unorm,
        usage: wgpu::TextureUsages::TEXTURE_BINDING | wgpu::TextureUsages::COPY_DST,
        label: Some(label),
        view_formats: &[wgpu::TextureFormat::Rgba8Unorm,]};
    let texture = device.create_texture(&texture_descriptor);

    // Upload to it
    queue.write_texture(
        wgpu::TexelCopyTextureInfo {
            texture: &texture,
            mip_level: 0,
            origin: wgpu::Origin3d::ZERO,
            aspect: wgpu::TextureAspect::All,
        },
        &converted,
        wgpu::TexelCopyBufferLayout {
            offset: 0,
            bytes_per_row: Some(4 * size.0),
            rows_per_image: Some(size.1),
        },
        texture_size);
    
    // Get a view of the texture
    let view = texture.create_view(&wgpu::TextureViewDescriptor::default());

    // Make a sampler
    let sampler_descriptor = wgpu::SamplerDescriptor {
        address_mode_u: wgpu::AddressMode::Repeat,
        address_mode_v: wgpu::AddressMode::Repeat,
        address_mode_w: wgpu::AddressMode::Repeat,
        mag_filter: wgpu::FilterMode::Linear,
        min_filter: wgpu::FilterMode::Nearest,
        mipmap_filter: wgpu::FilterMode::Nearest,
        ..Default::default()
    };
    let sampler = device.create_sampler(&sampler_descriptor);

    // Make a bind group for everything
    let mut builder = bind_group::Builder::new(device);
    builder.set_layout(layout);
    builder.add_material(&view, &sampler);
    let bind_group = builder.build(label);

    bind_group
    
}

pub fn new_cubemap(filename: &str, device: &wgpu::Device, 
    queue: &wgpu::Queue, label: &str) -> Texture {

    let suffixes: [&str; 6] = ["_right.png", "_left.png", "_back.png", "_front.png", "_top.png", "_bottom.png"];
    let angles: [i32; 6] = [270, 90, 180, 0, 0, 0];
    let mut texture_size: wgpu::Extent3d;

    // load first image and get size
    let full_filename = String::from(filename) + suffixes[0];
    let bytes = read_to_byte_vec("img/", &full_filename);
    let mut loaded_image = image::load_from_memory(&bytes).unwrap();
    if angles[0] == 90 {
        loaded_image = loaded_image.rotate90();
    }
    else if angles[0] == 180 {
        loaded_image = loaded_image.rotate180();
    }
    else if angles[0] == 270 {
        loaded_image = loaded_image.rotate270();
    }
    let converted = loaded_image.to_rgba8();
    let size = loaded_image.dimensions();
    texture_size = wgpu::Extent3d {
        width: size.0,
        height: size.1,
        depth_or_array_layers: 6};
    
    // Create the texture
    let texture_descriptor = wgpu::TextureDescriptor {
        size: texture_size,
        mip_level_count: 1,
        sample_count: 1,
        dimension: wgpu::TextureDimension::D2,
        format: wgpu::TextureFormat::Rgba8Unorm,
        usage: wgpu::TextureUsages::TEXTURE_BINDING | wgpu::TextureUsages::COPY_DST,
        label: Some(label),
        view_formats: &[wgpu::TextureFormat::Rgba8Unorm,]};
    let texture = device.create_texture(&texture_descriptor);

    texture_size.depth_or_array_layers = 1;

    // Upload to it
    let mut dst_offset = wgpu::Origin3d{x: 0, y: 0, z: 0};
    queue.write_texture(
        wgpu::TexelCopyTextureInfo {
            texture: &texture,
            mip_level: 0,
            origin: dst_offset,
            aspect: wgpu::TextureAspect::All,
        },
        &converted,
        wgpu::TexelCopyBufferLayout {
            offset: 0,
            bytes_per_row: Some(4 * size.0),
            rows_per_image: Some(size.1),
        },
        texture_size);
    device.poll(wgpu::MaintainBase::Wait).ok();
    dst_offset.z += 1;

    for i in 1..6 {
        // upload remaining images
        let full_filename = String::from(filename) + suffixes[i];
        let bytes = read_to_byte_vec("img/", &full_filename);
        let mut loaded_image = image::load_from_memory(&bytes).unwrap();
        if angles[i] == 90 {
            loaded_image = loaded_image.rotate90();
        }
        else if angles[i] == 180 {
            loaded_image = loaded_image.rotate180();
        }
        else if angles[i] == 270 {
            loaded_image = loaded_image.rotate270();
        }
        let converted = loaded_image.to_rgba8();

        // Upload to it
        queue.write_texture(
            wgpu::TexelCopyTextureInfo {
                texture: &texture,
                mip_level: 0,
                origin: dst_offset,
                aspect: wgpu::TextureAspect::All,
            },
            &converted,
            wgpu::TexelCopyBufferLayout {
                offset: 0,
                bytes_per_row: Some(4 * size.0),
                rows_per_image: Some(size.1),
            },
            texture_size);
        device.poll(wgpu::MaintainBase::Wait).ok();
        dst_offset.z += 1;
    }
    
    // Get a view of the texture
    let texture_view_descriptor = wgpu::TextureViewDescriptor{
        label: Some("Texture view descriptor"),
        format: Some(wgpu::TextureFormat::Rgba8Unorm),
        dimension: Some(wgpu::TextureViewDimension::Cube),
        usage: Some(wgpu::TextureUsages::TEXTURE_BINDING | wgpu::TextureUsages::COPY_DST),
        aspect: wgpu::TextureAspect::All,
        base_array_layer: 0,
        base_mip_level: 0,
        mip_level_count: Some(1),
        array_layer_count: Some(6)
    };
    let view = texture.create_view(&texture_view_descriptor);

    // Make a sampler
    let sampler_descriptor = wgpu::SamplerDescriptor {
        address_mode_u: wgpu::AddressMode::Repeat,
        address_mode_v: wgpu::AddressMode::Repeat,
        address_mode_w: wgpu::AddressMode::Repeat,
        mag_filter: wgpu::FilterMode::Linear,
        min_filter: wgpu::FilterMode::Nearest,
        mipmap_filter: wgpu::FilterMode::Nearest,
        ..Default::default()
    };
    let sampler = Some(device.create_sampler(&sampler_descriptor));

    Texture { texture, view, sampler }
    
}

pub fn new_color(color: &Vec4, device: &wgpu::Device, 
    label: &str, layout: &wgpu::BindGroupLayout) -> wgpu::BindGroup {

    let bytes: &[u8] = unsafe { any_as_u8_slice(color) };

    let buffer_descriptor = wgpu::util::BufferInitDescriptor { 
        label: Some("Model vertex & index buffer"), 
        contents: bytes,
        usage: wgpu::BufferUsages::UNIFORM };

    let buffer = device.create_buffer_init(&buffer_descriptor);

    // build bind groups
    let bind_group: wgpu::BindGroup;
    {
        let mut builder = bind_group::Builder::new(device);
        builder.set_layout(layout);
        builder.add_buffer(&buffer, 0);
        bind_group = builder.build(label);
    }

    bind_group
}