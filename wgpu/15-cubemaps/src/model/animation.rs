use std::collections::HashMap;

use crate::model::definitions;
use crate::model::common::ObjectType;
use crate::utility::file;
use crate::utility::math;

const ANIMATION_TARGET_ROTATION: u8 = 0;
const ANIMATION_TARGET_POS: u8 = 1;

pub fn load_skeleton_from_gltf(filename: &str) -> Skeleton {

    let full_contents = file::read_to_string("models/", filename);
    let data: serde_json::Value = serde_json::from_str(&full_contents).unwrap();

    let accessor_descriptors = &data["accessors"];

    let buffer_descriptor = &data["buffers"][0];
    let buffer_filename = buffer_descriptor["uri"].as_str().unwrap();
    let buffer: Vec<u8> = file::read_to_byte_vec("models/", buffer_filename);
    let buffer_views = data["bufferViews"].as_array().unwrap();

    let node_descriptors = &data["nodes"].as_array().unwrap();
    let skin_descriptor = &data["skins"][0];
    let inverse_bind_index: usize = skin_descriptor["inverseBindMatrices"]
                                                                .as_u64()
                                                                .unwrap().try_into().expect("error");
    let inverse_bind_accessor = &accessor_descriptors[inverse_bind_index];
    let inverse_bind_matrices = file::get_mat4s_from_buffer(&buffer, inverse_bind_accessor, buffer_views);
    let joint_indices = skin_descriptor["joints"].as_array().unwrap();

    let mut bones: Vec<Bone> = Vec::new();

    for i in 0 .. joint_indices.len() {
        let joint_index: usize = joint_indices[i].as_u64().unwrap().try_into().expect("error");
        let node_descriptor = &node_descriptors[joint_index];

        let rotation = file::vec4_from_json_value(node_descriptor, "rotation");
        let translation = file::vec3_from_json_value(node_descriptor, "translation");

        let mut children: Vec<u16> = Vec::new();
        let node_children = node_descriptor["children"].as_array();
        let name: String = String::from(node_descriptor["name"].as_str().unwrap());
        if !node_children.is_none() {
            let node_children = node_children.unwrap();
            for j in 0 .. node_children.len() {
                let node_id: u16 = node_children[j].as_u64().unwrap() as u16;
                let joint_id: u16 = file::find_index(joint_indices, node_id);
                children.push(joint_id);
            }
        }

        let inverse_bind_matrix = inverse_bind_matrices[i];
        bones.push(Bone::new(rotation, translation, children,
                            inverse_bind_matrix, name));
    }

    println!("Made Skeleton");

    Skeleton::new(bones)
}

pub fn load_animations_from_gltf(filename: &str) -> HashMap<u8, AnimationComponent> {
    let full_contents = file::read_to_string("models/", filename);
    let data: serde_json::Value = serde_json::from_str(&full_contents).unwrap();

    let animation_descriptors = data["animations"].as_array().unwrap();
    let accessor_descriptors = data["accessors"].as_array().unwrap();
    let buffer_views = data["bufferViews"].as_array().unwrap();
    let skin_descriptor = &data["skins"][0];
    let animation_codes = &definitions::get_animation_lookup()[&ObjectType::Girl];
    let joint_indices = skin_descriptor["joints"].as_array().unwrap();

    let buffer_descriptor = &data["buffers"][0];
    let buffer_filename = buffer_descriptor["uri"].as_str().unwrap();
    let buffer: Vec<u8> = file::read_to_byte_vec("models/", buffer_filename);

    make_animations(animation_codes,
                    animation_descriptors,
                    accessor_descriptors,
                    buffer_views,
                    &buffer,
                    joint_indices)
}

pub fn make_animations(animation_codes: &HashMap<String, u8>,
                    animation_descriptors: &Vec<serde_json::Value>,
                    accessor_descriptors: &Vec<serde_json::Value>,
                    buffer_views: &Vec<serde_json::Value>,
                    buffer: &Vec<u8>,
                    joint_indices: &Vec<serde_json::Value>) -> HashMap<u8, AnimationComponent> {
    
    let mut animations: HashMap<u8, AnimationComponent> = HashMap::new();
    
    for i in 0 .. animation_descriptors.len() {
        let animation_descriptor = &animation_descriptors[i];
        let sampler_lookup = parse_sampler_types(animation_descriptor);
        let channels = make_animation_channels(animation_descriptor, joint_indices, &sampler_lookup);
        let translation_samplers = make_translation_samplers(animation_descriptor, accessor_descriptors, buffer_views, buffer);
        let rotation_samplers = make_rotation_samplers(animation_descriptor, accessor_descriptors, buffer_views, buffer);

        let animation_name = animation_descriptor["name"].as_str().unwrap();
        let animation_type = animation_codes[animation_name];
        animations.insert(animation_type, AnimationComponent::new(channels, translation_samplers, rotation_samplers));
    }

    println!("Made animations");

    animations
    
}

pub fn parse_sampler_types(animation_descriptor: &serde_json::Value) -> HashMap<u64, usize> {
    
    let channel_descriptors = animation_descriptor["channels"].as_array().unwrap();
    let mut lookup: HashMap<u64, usize> = HashMap::new();
    let mut translation_count = 0;
    let mut rotation_count = 0;

    for i in 0 .. channel_descriptors.len() {
        let channel_descriptor = &channel_descriptors[i];
        let target_attribute = channel_descriptor["target"]["path"].as_str().unwrap();
        let sampler_index = channel_descriptor["sampler"].as_u64().unwrap();
        if target_attribute == "translation" {
            lookup.insert(sampler_index, translation_count);
            translation_count = translation_count + 1;
        }
        else if target_attribute == "rotation" {
            lookup.insert(sampler_index, rotation_count);
            rotation_count = rotation_count + 1;
        }
    }

    lookup
}

pub fn make_animation_channels(animation_descriptor: &serde_json::Value,
                            joint_indices: &Vec<serde_json::Value>,
                            sampler_lookup: &HashMap<u64, usize>) -> Vec<AnimationChannel> {
    
    let channel_descriptors = animation_descriptor["channels"].as_array().unwrap();
    let mut channels: Vec<AnimationChannel> = Vec::new();
    channels.reserve(channel_descriptors.len());

    for i in 0 .. channel_descriptors.len() {
        let channel_descriptor = &channel_descriptors[i];
        let joint_id = channel_descriptor["target"]["node"].as_u64().unwrap();
        let bone_index = file::find_index(joint_indices, joint_id as u16) as usize;
        let target_attribute = channel_descriptor["target"]["path"].as_str().unwrap();
        let target = match target_attribute {
            "rotation" => ANIMATION_TARGET_ROTATION,
            "translation" => ANIMATION_TARGET_POS,
            _ => 255
        };
        if target_attribute == "scale" {
            continue;
        }
        let sampler_index = channel_descriptor["sampler"].as_u64().unwrap();
        //println!("Requesting key {}", sampler_index);
        let sampler_index = sampler_lookup[&sampler_index];

        channels.push(AnimationChannel {sampler_index, bone_index, target});
    }

    channels
}

pub fn make_translation_samplers(
    animation_descriptor: &serde_json::Value, 
    accessor_descriptors: &Vec<serde_json::Value>, 
    buffer_views: &Vec<serde_json::Value>, 
    buffer: &Vec<u8>) -> Vec<TranslationSampler> {
    
    let mut samplers: Vec<TranslationSampler> = Vec::new();
    let channel_descriptors = animation_descriptor["channels"].as_array().unwrap();
    let sampler_descriptors = animation_descriptor["samplers"].as_array().unwrap();

    for i in 0 .. channel_descriptors.len() {
        let channel_descriptor = &channel_descriptors[i];
        let target_attribute = channel_descriptor["target"]["path"].as_str().unwrap();
        if target_attribute != "translation" {
            continue;
        }
        
        let sampler_index = channel_descriptor["sampler"].as_u64().unwrap() as usize;
        let sampler_descriptor = &sampler_descriptors[sampler_index];

        let timestamp_accessor_index = sampler_descriptor["input"].as_u64().unwrap() as usize;
        let timestamp_accessor = &accessor_descriptors[timestamp_accessor_index];
        let timestamps = file::get_f32s_from_buffer(buffer, timestamp_accessor, buffer_views);
        let timesampler = TimeSampler {timestamps};

        let value_accessor_index = sampler_descriptor["output"].as_u64().unwrap() as usize;
        let value_accessor = &accessor_descriptors[value_accessor_index];
        let values = file::get_vec3s_from_buffer(buffer, value_accessor, buffer_views);

        samplers.push(TranslationSampler { values, timesampler });
    }

    samplers
}

pub fn make_rotation_samplers(
    animation_descriptor: &serde_json::Value, 
    accessor_descriptors: &Vec<serde_json::Value>, 
    buffer_views: &Vec<serde_json::Value>, 
    buffer: &Vec<u8>) -> Vec<RotationSampler> {
    
    let mut samplers: Vec<RotationSampler> = Vec::new();
    let channel_descriptors = animation_descriptor["channels"].as_array().unwrap();
    let sampler_descriptors = animation_descriptor["samplers"].as_array().unwrap();

    for i in 0 .. channel_descriptors.len() {
        let channel_descriptor = &channel_descriptors[i];
        let target_attribute = channel_descriptor["target"]["path"].as_str().unwrap();
        if target_attribute != "rotation" {
            continue;
        }
        
        let sampler_index = channel_descriptor["sampler"].as_u64().unwrap() as usize;
        let sampler_descriptor = &sampler_descriptors[sampler_index];

        let timestamp_accessor_index = sampler_descriptor["input"].as_u64().unwrap() as usize;
        let timestamp_accessor = &accessor_descriptors[timestamp_accessor_index];
        let timestamps = file::get_f32s_from_buffer(buffer, timestamp_accessor, buffer_views);
        let timesampler = TimeSampler {timestamps};

        let value_accessor_index = sampler_descriptor["output"].as_u64().unwrap() as usize;
        let value_accessor = &accessor_descriptors[value_accessor_index];
        let values = file::get_vec4s_from_buffer(buffer, value_accessor, buffer_views);

        samplers.push(RotationSampler { values, timesampler });
    }

    samplers
}

pub struct Bone {
    rotation: glm::Vec4,
    translation: glm::Vec3,
    child_indices: Vec<u16>,
    pub inverse_bind_matrix: glm::Mat4,
    pub name: String,
}

impl Bone {
    pub fn new(rotation: glm::Vec4,
            translation: glm::Vec3,
            child_indices: Vec<u16>,
            inverse_bind_matrix: glm::Mat4,
            name: String) -> Self {

        Self {
            rotation,
            translation,
            child_indices,
            inverse_bind_matrix,
            name
        }
    }

    pub fn get_transform(&mut self) -> glm::Mat4 {
        math::from_translation(&self.translation)
            * math::get_matrix_from_quaternion(&self.rotation)
    }
}

pub struct Skeleton {
    bones: Vec<Bone>,
    pub transforms: Vec<glm::Mat4>,
    parent_index: HashMap<usize, usize>,
    pub sockets: HashMap<String, glm::Mat4>
}

impl Skeleton {
    pub fn new(bones: Vec<Bone>) -> Self {

        let mut transforms: Vec<glm::Mat4> = Vec::new();
        transforms.resize(bones.len(), math::identity());

        let mut parent_index: HashMap<usize, usize> = HashMap::new();
        let mut sockets: HashMap<String, glm::Mat4> = HashMap::new();
        for i in 0 .. bones.len() {
            let bone = &bones[i];
            for j in 0 .. bone.child_indices.len() {
                let child_index = bone.child_indices[j] as usize;
                parent_index.insert(child_index, i);
            }
            sockets.insert(bone.name.clone(), math::identity());
        }

        Self {bones, transforms, parent_index, sockets}
    }

    pub fn update(&mut self) {

        // For each bone, calculate its local transform, then maybe incorporate parent transform
        for i in 0 .. self.bones.len() {
            let bone = &mut self.bones[i];
            let transform = bone.get_transform();
            self.transforms[i] = transform;

            if self.parent_index.contains_key(&i) {
                // parent transform
                let j = self.parent_index[&i];
                self.transforms[i] = self.transforms[j] * self.transforms[i];
            }

            // Write socket transform
            self.sockets.insert(bone.name.clone(), self.transforms[i]);
        }

        // pre multiply inverse bind matrix
        for i in 0 .. self.bones.len() {
            let bone = &self.bones[i];
            self.transforms[i] = self.transforms[i] * bone.inverse_bind_matrix;
        }
    }
}

pub struct AnimationChannel {
    pub sampler_index: usize,
    pub bone_index: usize,
    pub target: u8,
}

pub struct TimeSampler {
    timestamps: Vec<f32>,
}

impl TimeSampler {

    fn get_duration(&self) -> f32 {
        *self.timestamps.last().unwrap()
    }

    pub fn find_span(&self, mut t: f32) -> (usize, usize, f32) {

        let duration = self.get_duration();
        while t > duration {
            t = t - duration;
        }

        let timestep_count = self.timestamps.len();
        let mut index_a = timestep_count - 1;

        let mut searching = true;
        while searching {
            searching = t > self.timestamps[(index_a + 1) % timestep_count];
            if searching {
                index_a = index_a + 1;
            }
        }

        index_a = index_a % timestep_count;
        let mut time_a = self.timestamps[index_a];
        let mut index_b = (index_a + 1) % timestep_count;
        let mut time_b = self.timestamps[index_b];

        if time_a > time_b {
            t = t + duration;
            time_b = time_b + duration;
        }

        if time_a == time_b {
            t = t - duration;
            index_a = (index_a + 1) % timestep_count;
            index_b = (index_b + 1) % timestep_count;
            time_a = self.timestamps[index_a];
            time_b = self.timestamps[index_b];
        }

        let t = (t - time_a) / (time_b - time_a);

        (index_a, index_b, t)
    }
}

pub struct TranslationSampler {
    values: Vec<glm::Vec3>,
    pub timesampler: TimeSampler
}

impl TranslationSampler {

    pub fn lerp(&self, t: f32) -> glm::Vec3 {
        let (index_a, index_b, t) = self.timesampler.find_span(t);

        self.values[index_a] * (1.0 - t) + self.values[index_b] * t
    }
}

pub struct RotationSampler {
    values: Vec<glm::Vec4>,
    pub timesampler: TimeSampler,
}

impl RotationSampler {

    pub fn slerp(&self, t: f32) -> glm::Vec4 {
        let (index_a, index_b, t) = self.timesampler.find_span(t);

        math::quaternion_slerp(self.values[index_a], self.values[index_b], t)
    }
}

pub struct AnimationComponent {
    channels: Vec<AnimationChannel>,
    translation_samplers: Vec<TranslationSampler>,
    rotation_samplers: Vec<RotationSampler>,
    duration: f32,
}

impl AnimationComponent {

    pub fn new(channels: Vec<AnimationChannel>,
                translation_samplers: Vec<TranslationSampler>,
                rotation_samplers: Vec<RotationSampler>) -> Self {
        
        let mut duration: f32 = 0.0;
        
        for sampler in &translation_samplers {
            duration = glm::max(duration, sampler.timesampler.get_duration());
        }

        for sampler in &rotation_samplers {
            duration = glm::max(duration, sampler.timesampler.get_duration());
        }

        Self {channels, translation_samplers, rotation_samplers, duration}
    }
    
    pub fn has_overrun(&self, t: f32) -> bool {
        t >= self.duration
    }

    pub fn get_duration(&self) -> f32 {
        self.duration
    }

    pub fn skin(&self, skeleton: &mut Skeleton, t: f32) {

        for channel in &self.channels {
            let bone = &mut skeleton.bones[channel.bone_index];
            match channel.target {
                ANIMATION_TARGET_POS => {
                    let sampler = &self.translation_samplers[channel.sampler_index];
                    bone.translation = sampler.lerp(t);
                },
                ANIMATION_TARGET_ROTATION => {
                    let sampler = &self.rotation_samplers[channel.sampler_index];
                    bone.rotation = sampler.slerp(t);
                },
                _ => {}
            }
        }
    }
}
