use glm::{Vec3, min, max, cross, normalize, radians, cos, sin};

pub struct Object {
    pub position: Vec3,
    pub angle: f32,
}

pub struct Camera {
    pub position: Vec3,
    pub forwards: Vec3,
    pub right: Vec3,
    pub up: Vec3,
    yaw: f32,
    pitch: f32,
}

impl Camera {

    pub fn new() -> Self {
        let position = Vec3::new(-5.0, 0.0, 2.0);
        let yaw: f32 = 0.0;
        let pitch: f32 = 0.0;

        let forwards = Vec3::new(1.0, 0.0 ,0.0);
        let right = Vec3::new(0.0, -1.0 ,0.0);
        let up = Vec3::new(0.0, 0.0 ,1.0);

        Camera { position, yaw, pitch, forwards, right, up }
    }

    pub fn spin(&mut self, d_yaw: f32, d_pitch: f32) {

        self.yaw = self.yaw + d_yaw;
        if self.yaw > 360.0 {
            self.yaw = self.yaw - 360.0;
        }
        if self.yaw < 0.0 {
            self.yaw = self.yaw + 360.0;
        }

        self.pitch = min(89.0, max(-89.0, self.pitch + d_pitch));

        let c = cos(radians(self.yaw));
        let s = sin(radians(self.yaw));
        let c2 = cos(radians(self.pitch));
        let s2 = sin(radians(self.pitch));

        self.forwards.x = c * c2;
        self.forwards.y = s * c2;
        self.forwards.z = s2;

        self.up.x = 0.0;
        self.up.y = 0.0;
        self.up.z = 1.0;

        self.right = normalize(cross(self.forwards, self.up));

        self.up = normalize(cross(self.right, self.forwards));
    }

    pub fn walk(&mut self, d_right: f32, d_forwards: f32) {

        let z : f32 = self.position.z;
        self.position = self.position + self.right * d_right + self.forwards * d_forwards;
        self.position.z = z;
    }
}