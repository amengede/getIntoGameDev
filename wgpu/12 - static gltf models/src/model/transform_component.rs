use glm::*;

pub struct TransformComponent {
    pub position: Vec3,
    pub eulers: Vec3,
    pub scale: f32,
}

fn get_rotation_matrix(eulers: &Vec3) -> Mat4 {

    // Construct quaternion from eulers
    let half_roll = 0.5 * eulers[0].to_radians();
    let s_r = sin(half_roll);
    let c_r = cos(half_roll);

    let half_pitch = 0.5 * eulers[1].to_radians();
    let s_p = sin(half_pitch);
    let c_p = cos(half_pitch);

    let half_yaw = 0.5 * eulers[2].to_radians();
    let s_y = sin(half_yaw);
    let c_y = cos(half_yaw);

    let mut q_x = (s_r * c_p * c_y) + (c_r * s_p * s_y);
    let mut q_y = (c_r * s_p * c_y) - (s_r * c_p * s_y);
    let mut q_z = (c_r * c_p * s_y) + (s_r * s_p * c_y);
    let mut q_w = (c_r * c_p * c_y) - (s_r * s_p * s_y);

    let norm = sqrt(q_x * q_x + q_y * q_y + q_z * q_z + q_w * q_w);
    q_x = q_x / norm;
    q_y = q_y / norm;
    q_z = q_z / norm;
    q_w = q_w / norm;

    // Get matrix from quaternion
    let sqw = q_w * q_w;
    let sqx = q_x * q_x;
    let sqy = q_y * q_y;
    let sqz = q_z * q_z;
    let qxy = q_x * q_y;
    let qzw = q_z * q_w;
    let qxz = q_x * q_z;
    let qyw = q_y * q_w;
    let qyz = q_y * q_z;
    let qxw = q_x * q_w;

    let invs = 1.0 / (sqx + sqy + sqz + sqw);
    let m00 = ( sqx - sqy - sqz + sqw) * invs;
    let m11 = (-sqx + sqy - sqz + sqw) * invs;
    let m22 = (-sqx - sqy + sqz + sqw) * invs;
    let m10 = 2.0 * (qxy + qzw) * invs;
    let m01 = 2.0 * (qxy - qzw) * invs;
    let m20 = 2.0 * (qxz - qyw) * invs;
    let m02 = 2.0 * (qxz + qyw) * invs;
    let m21 = 2.0 * (qyz + qxw) * invs;
    let m12 = 2.0 * (qyz - qxw) * invs;

    mat4(
        m00, m10, m20, 0.0,
        m01, m11, m21, 0.0,
        m02, m12, m22, 0.0,
        0.0, 0.0, 0.0, 1.0
    )
}

pub fn from_scale(scale: f32) -> Mat4 {
    mat4(
        scale, 0.0, 0.0, 0.0,
        0.0, scale, 0.0, 0.0,
        0.0, 0.0, scale, 0.0,
        0.0, 0.0, 0.0, 1.0
    )
}

pub fn from_translation(v: &Vec3) -> Mat4 {
    mat4(
        1.0, 0.0, 0.0, 0.0,
        0.0, 1.0, 0.0, 0.0,
        0.0, 0.0, 1.0, 0.0,
        v[0], v[1], v[2], 1.0
    )
}

impl TransformComponent {
    pub fn get_transform(&self) -> Mat4 {
        from_scale(self.scale)
        * get_rotation_matrix(&self.eulers)
        * from_translation(&self.position)
    }
}