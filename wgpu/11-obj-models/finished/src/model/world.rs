use std::collections::HashMap;
use glfw::Window;
use crate::model::game_objects::{Camera, Object};

pub struct World {
    pub quads: Vec<Object>,
    pub tris: Vec<Object>,
    pub camera: Camera,
    pub keys: HashMap<glfw::Key, bool>,
}

impl World {

    pub fn new() -> Self {
        let mut world = World { 
            quads: Vec::new(), 
            tris: Vec::new(), 
            camera: Camera::new(),
            keys: HashMap::new() };
        
        world.keys.insert(glfw::Key::W, false);
        world.keys.insert(glfw::Key::A, false);
        world.keys.insert(glfw::Key::S, false);
        world.keys.insert(glfw::Key::D, false);

        world
    }

    pub fn set_key(&mut self, key: glfw::Key, state: bool) {
        self.keys.insert(key, state);
    }
    pub fn update(&mut self, dt: f32, window: &mut Window) {

        for i in 0..self.tris.len() {
            self.tris[i].angle = self.tris[i].angle + 0.001 * dt;
            if self.tris[i].angle > 360.0 {
                self.tris[i].angle -= 360.0;
            }
        }

        let mouse_pos = window.get_cursor_pos();
        window.set_cursor_pos(400.0, 300.0);
        let dx = (-40.0 * (mouse_pos.0 - 400.0) / 400.0) as f32;
        let dy = (-40.0 * (mouse_pos.1 - 300.0) / 300.0) as f32;
        self.camera.spin(dx, dy);

        let mut d_right: f32 = 0.0;
        let mut d_forwards: f32 = 0.0;

        if self.keys[&glfw::Key::W] {
            d_forwards = d_forwards + 0.1;
        }
        if self.keys[&glfw::Key::A] {
            d_right = d_right - 0.1;
        }
        if self.keys[&glfw::Key::S] {
            d_forwards = d_forwards - 0.1;
        }
        if self.keys[&glfw::Key::D] {
            d_right = d_right + 0.1;
        }
        self.camera.walk(d_right, d_forwards);
    }
}