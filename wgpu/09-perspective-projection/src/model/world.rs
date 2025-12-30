use super::game_objects::Object;

pub struct World {
    pub quads: Vec<Object>,
    pub tris: Vec<Object>,
}

impl World {

    pub fn new() -> Self {
        World { quads: Vec::new(), tris: Vec::new() }
    }

    pub fn update(&mut self, dt: f32) {

        for i in 0..self.tris.len() {
            self.tris[i].angle = self.tris[i].angle + 0.001 * dt;
            if self.tris[i].angle > 360.0 {
                self.tris[i].angle -= 360.0;
            }
        }
    }
}