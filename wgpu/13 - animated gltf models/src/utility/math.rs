use glm::*;

pub fn quaternion_from_eulers(eulers: &Vec3) -> Vec4 {

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

    Vec4::new(q_x, q_y, q_z, q_w)
}

pub fn get_matrix_from_quaternion(q: &Vec4) -> Mat4 {

    let q_x = q[0];
    let q_y = q[1];
    let q_z = q[2];
    let q_w = q[3];

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

pub fn get_euler_rotation(eulers: &Vec3) -> Mat4 {
    let quaternion = quaternion_from_eulers(eulers);
    get_matrix_from_quaternion(&quaternion)
}

pub fn z_axis_rotation(angle: f32) -> Mat4 {
    let eulers = Vec3::new(0.0, 0.0, angle);
    let quaternion = quaternion_from_eulers(&eulers);
    get_matrix_from_quaternion(&quaternion)
}

pub fn identity() -> Mat4 {
    let c0 = Vec4::new(1.0, 0.0, 0.0, 0.0);
    let c1 = Vec4::new(0.0, 1.0, 0.0, 0.0);
    let c2 = Vec4::new(0.0, 0.0, 1.0, 0.0);
    let c3 = Vec4::new(0.0, 0.0, 0.0, 1.0);

    Mat4::new(c0, c1, c2, c3)
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

pub fn quaternion_slerp(q1: Vec4, q2: Vec4, t: f32) -> Vec4 {

    let mut dot_product = dot(q1, q2);
    let mut q3 = q2;
    if dot_product < 0.0 {
        dot_product = -dot_product;
        q3 = -q3;
    }

    if dot_product < 0.95 {
        let angle = acos(dot_product);
        (q1 * sin(angle * (1.0 - t)) + q3 * sin(angle * t)) / sin(angle)
    }
    else {
        q1 * (1.0 - t) + q3 * t
    }
}
