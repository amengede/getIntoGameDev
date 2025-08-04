use std::env::current_dir;

use super::bind_group;

pub struct Material {
    pub bind_group: wgpu::BindGroup,
}

impl Material {

    pub fn new(filename: &str, device: &wgpu::Device, queue: &wgpu::Queue, label: &str, layout: &wgpu::BindGroupLayout) -> Self {

        // Get absolute filepath from relative one
        let mut filepath = current_dir().unwrap();
        filepath.push("src/");
        filepath.push(filename);
        let filepath = filepath.into_os_string().into_string().unwrap();

        let bytes = std::fs::read(filepath).unwrap();
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
            wgpu::ImageCopyTexture {
                texture: &texture,
                mip_level: 0,
                origin: wgpu::Origin3d::ZERO,
                aspect: wgpu::TextureAspect::All,
            },
            &converted,
            wgpu::ImageDataLayout {
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

        Material {bind_group: bind_group}
        
    }
}