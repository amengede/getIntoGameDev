use super::transform_component::TransformComponent;
use super::animation::{Skeleton, load_skeleton_from_gltf};
use super::animation::AnimationComponent;
use std::collections::HashMap;
use super::definitions;

pub struct Character {
    pub transform_component: TransformComponent,
    pub skeleton_component: Skeleton,
    current_animation: u8,
    animation_t: f32,
}

impl Character {
    pub fn new(filename: &str, pos: glm::Vec3, eulers: glm::Vec3, scale: f32) -> Self {
        
        let transform_component = TransformComponent{
            position: pos,
            eulers,
            scale
        };

        let skeleton_component = load_skeleton_from_gltf(filename);

        let current_animation: u8 = definitions::ANIMATION_TYPE_WALK;
        let animation_t: f32 = 0.0;

        Self {transform_component, skeleton_component, current_animation, animation_t}
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