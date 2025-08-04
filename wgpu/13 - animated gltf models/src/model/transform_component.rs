use glm::*;
use crate::utility::math::*;

pub struct TransformComponent {
    pub position: Vec3,
    pub eulers: Vec3,
    pub scale: f32,
}

impl TransformComponent {
    pub fn get_transform(&self) -> Mat4 {
        from_translation(&self.position)
        * get_euler_rotation(&self.eulers)
        * from_scale(self.scale)
    }
}