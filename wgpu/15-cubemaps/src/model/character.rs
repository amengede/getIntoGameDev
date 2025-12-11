use super::transform_component::TransformComponent;
use super::animation::{Skeleton, load_skeleton_from_gltf};
use super::animation::AnimationComponent;
use std::collections::HashMap;
use super::definitions;
use super::common::ObjectType;

pub struct Character {
    /// Character's position and rotation
    pub transform_component: TransformComponent,
    /// Orientation of all character's bones
    pub skeleton_component: Skeleton,
    /// The current animation applied to the character
    current_animation: u8,
    /// Current animation's time (in seconds)
    animation_t: f32,
    /// props attached to the character. keys: bone names, values: objects
    pub attachments: HashMap<String, ObjectType>,
    /// Type of object used to represent this character
    pub object_type: ObjectType
}

impl Character {
    pub fn new(
        filename: &str, pos: glm::Vec3, eulers: glm::Vec3, 
        scale: f32, object_type: ObjectType) -> Self {
        
        let transform_component = TransformComponent{
            position: pos,
            eulers,
            scale
        };

        let skeleton_component = load_skeleton_from_gltf(filename);

        let current_animation: u8 = definitions::ANIMATION_TYPE_WALK;
        let animation_t: f32 = 0.0;

        let attachments: HashMap<String, ObjectType> = HashMap::new();

        Self {
            transform_component, skeleton_component,
            current_animation, animation_t,
            attachments, object_type}
    }

    pub fn add_attachment(&mut self, socket_name: String, object_type: ObjectType) {
        
        self.attachments.insert(socket_name, object_type);
    }

    pub fn update(&mut self, dt: f32, animations: &HashMap<u8, AnimationComponent>) {
        let animation = &animations[&self.current_animation];

        self.animation_t += 0.001 * dt;
        if animation.has_overrun(self.animation_t) {
            self.animation_t = self.animation_t - animation.get_duration();
        }

        animation.skin(&mut self.skeleton_component, self.animation_t);
        self.skeleton_component.update();
    }
}