use std::{env::current_dir, fs::File};
use std::fs;
use std::io::Read;

pub fn find_index(values: &Vec<serde_json::Value>, value: u16) -> u16 {
    
    for i in 0 .. values.len() {
        if values[i].as_u64().unwrap() as u16 == value {
            return i as u16;
        }
    }
    return 0;
}

pub fn read_to_string(folder: &str, filename: &str) -> String {
    let mut full_filepath = current_dir().unwrap();
    full_filepath.push(folder);
    full_filepath.push(filename);
    let filepath_str = full_filepath.into_os_string().into_string().unwrap();
    fs::read_to_string(filepath_str).expect("Can't read file to string!")
}

pub fn read_to_byte_vec(folder: &str, filename: &str) -> Vec<u8> {
    let mut full_filepath = current_dir().unwrap();
    full_filepath.push(folder);
    full_filepath.push(filename);
    let filepath_str = full_filepath.into_os_string().into_string().unwrap();
    let mut bin_file = File::open(filepath_str).expect("Error");
    let mut buffer: Vec<u8> = Vec::new();
    bin_file.read_to_end(&mut buffer).ok();
    buffer
}

pub fn get_mat4s_from_buffer(buffer: &Vec<u8>,
    accessor: &serde_json::Value, buffer_views: &Vec<serde_json::Value>) -> Vec<glm::Mat4> {
    let buffer_view_index: usize = accessor["bufferView"].as_u64().unwrap() as usize;
    let buffer_view = &buffer_views[buffer_view_index];
    let offset: usize = buffer_view["byteOffset"].as_u64().unwrap() as usize;
    let count: usize = accessor["count"].as_u64().unwrap() as usize;
    let mut result: Vec<glm::Mat4> = Vec::new();
    result.reserve(count);

    for i in 0 .. count {
        result.push(get_mat4(buffer, offset + 64 * i));
    }

    result
}

pub fn get_mat4(buffer: &Vec<u8>, offset: usize) -> glm::Mat4 {
    let c0 = get_vec4(buffer, offset);
    let c1 = get_vec4(buffer, offset + 16);
    let c2 = get_vec4(buffer, offset + 32);
    let c3 = get_vec4(buffer, offset + 48);
    glm::Mat4::new(c0, c1, c2, c3)
}

pub fn vec4_from_json_value(node: &serde_json::Value, attribute_name: &str) -> glm::Vec4 {
    let temp_floats = node[attribute_name].as_array();

    if temp_floats.is_none() {
        // default value
        return glm::Vec4::new(0.0, 0.0, 0.0, 1.0);
    }

    let temp_floats = temp_floats.unwrap();
    let x: f32 = temp_floats[0].as_f64().unwrap() as f32;
    let y: f32 = temp_floats[1].as_f64().unwrap() as f32;
    let z: f32 = temp_floats[2].as_f64().unwrap() as f32;
    let w: f32 = temp_floats[3].as_f64().unwrap() as f32;
    glm::Vec4::new(x, y, z, w)
}

pub fn get_vec4s_from_buffer(buffer: &Vec<u8>,
    accessor: &serde_json::Value, buffer_views: &Vec<serde_json::Value>) -> Vec<glm::Vec4> {
    let buffer_view_index: usize = accessor["bufferView"].as_u64().unwrap() as usize;
    let buffer_view = &buffer_views[buffer_view_index];
    let offset: usize = buffer_view["byteOffset"].as_u64().unwrap() as usize;
    let count: usize = accessor["count"].as_u64().unwrap() as usize;
    let mut result: Vec<glm::Vec4> = Vec::new();
    result.reserve(count);

    for i in 0 .. count {
        result.push(get_vec4(buffer, offset + 16 * i));
    }

    result
}

pub fn get_vec4(buffer: &Vec<u8>, offset: usize) -> glm::Vec4 {
    let x = f32::from_le_bytes(get_u8_4(buffer, offset));
    let y = f32::from_le_bytes(get_u8_4(buffer, offset + 4));
    let z = f32::from_le_bytes(get_u8_4(buffer, offset + 8));
    let w = f32::from_le_bytes(get_u8_4(buffer, offset + 12));
    glm::vec4(x, y, z, w)
}

pub fn vec3_from_json_value(node: &serde_json::Value, attribute_name: &str) -> glm::Vec3 {
    let temp_floats = node[attribute_name].as_array();

    if temp_floats.is_none() {
        // default value
        return glm::Vec3::new(0.0, 0.0, 0.0);
    }

    let temp_floats = temp_floats.unwrap();
    let x: f32 = temp_floats[0].as_f64().unwrap() as f32;
    let y: f32 = temp_floats[1].as_f64().unwrap() as f32;
    let z: f32 = temp_floats[2].as_f64().unwrap() as f32;
    glm::Vec3::new(x, y, z)
}

pub fn get_vec3s_from_buffer(buffer: &Vec<u8>,
    accessor: &serde_json::Value, buffer_views: &Vec<serde_json::Value>) -> Vec<glm::Vec3> {
    
    let buffer_view_index: usize = accessor["bufferView"].as_u64().unwrap() as usize;
    let buffer_view = &buffer_views[buffer_view_index];
    let offset: usize = buffer_view["byteOffset"].as_u64().unwrap() as usize;
    let count: usize = accessor["count"].as_u64().unwrap() as usize;
    let mut result: Vec<glm::Vec3> = Vec::new();
    result.reserve(count);

    for i in 0 .. count {
        result.push(get_vec3(buffer, offset + 12 * i));
    }

    result
}

pub fn get_vec3(buffer: &Vec<u8>, offset: usize) -> glm::Vec3 {
    let x = f32::from_le_bytes(get_u8_4(buffer, offset));
    let y = f32::from_le_bytes(get_u8_4(buffer, offset + 4));
    let z = f32::from_le_bytes(get_u8_4(buffer, offset + 8));
    glm::vec3(x, y, z)
}

pub fn get_vec2s_from_buffer(buffer: &Vec<u8>,
    accessor: &serde_json::Value, buffer_views: &Vec<serde_json::Value>) -> Vec<glm::Vec2> {
    
    let buffer_view_index: usize = accessor["bufferView"].as_u64().unwrap() as usize;
    let buffer_view = &buffer_views[buffer_view_index];
    let offset: usize = buffer_view["byteOffset"].as_u64().unwrap() as usize;
    let count: usize = accessor["count"].as_u64().unwrap() as usize;
    let mut result: Vec<glm::Vec2> = Vec::new();
    result.reserve(count);

    for i in 0 .. count {
        result.push(get_vec2(buffer, offset + 8 * i));
    }

    result
}

pub fn get_vec2(buffer: &Vec<u8>, offset: usize) -> glm::Vec2 {
    let x = f32::from_le_bytes(get_u8_4(buffer, offset));
    let y = f32::from_le_bytes(get_u8_4(buffer, offset + 4));
    glm::vec2(x, y)
}

pub fn get_u16s_from_buffer(buffer: &Vec<u8>,
    accessor: &serde_json::Value, buffer_views: &Vec<serde_json::Value>) -> Vec<u16> {
    
    let buffer_view_index: usize = accessor["bufferView"].as_u64().unwrap() as usize;
    let buffer_view = &buffer_views[buffer_view_index];
    let offset: usize = buffer_view["byteOffset"].as_u64().unwrap() as usize;
    let count: usize = accessor["count"].as_u64().unwrap() as usize;
    let mut result: Vec<u16> = Vec::new();
    result.reserve(count);

    for i in 0 .. count {
        result.push(get_u16(buffer, offset + 2 * i));
    }

    result
}

pub fn get_u16(buffer: &Vec<u8>, offset: usize) -> u16 {
    u16::from_le_bytes(get_u8_2(buffer, offset))
}

pub fn get_f32s_from_buffer(buffer: &Vec<u8>,
    accessor: &serde_json::Value, buffer_views: &Vec<serde_json::Value>) -> Vec<f32> {
    
    let buffer_view_index: usize = accessor["bufferView"].as_u64().unwrap() as usize;
    let buffer_view = &buffer_views[buffer_view_index];
    let offset: usize = buffer_view["byteOffset"].as_u64().unwrap() as usize;
    let count: usize = accessor["count"].as_u64().unwrap() as usize;
    let mut result: Vec<f32> = Vec::new();
    result.reserve(count);

    for i in 0 .. count {
        result.push(get_f32(buffer, offset + 4 * i));
    }

    result
}

pub fn get_f32(buffer: &Vec<u8>, offset: usize) -> f32 {
    f32::from_le_bytes(get_u8_4(buffer, offset))
}

pub fn get_u8_4s_from_buffer(buffer: &Vec<u8>,
    accessor: &serde_json::Value, buffer_views: &Vec<serde_json::Value>) -> Vec<[u8; 4]> {

    let buffer_view_index: usize = accessor["bufferView"].as_u64().unwrap() as usize;
    let buffer_view = &buffer_views[buffer_view_index];
    let offset: usize = buffer_view["byteOffset"].as_u64().unwrap() as usize;
    let count: usize = accessor["count"].as_u64().unwrap() as usize;
    let mut result: Vec<[u8; 4]> = Vec::new();
    result.reserve(count);

    for i in 0 .. count {
        result.push(get_u8_4(buffer, offset + 4 * i));
    }

    result
}

pub fn get_u8_4(buffer: &Vec<u8>, offset: usize) -> [u8; 4] {
    buffer[offset .. offset + 4].try_into().expect("error!")
}

pub fn get_u8_2(buffer: &Vec<u8>, offset: usize) -> [u8; 2] {
    buffer[offset .. offset + 2].try_into().expect("error!")
}