#include "math.h"

float deg2rad(const float& theta) {
	return theta * (3.1415926f / 180.0f);
}
//-------------------    Vec2    ---------------------------//
#pragma region

std::ostream& operator<<(std::ostream& os, const vec2& vector) {
	os << "<"
		<< vector.elements[0]
		<< ", " << vector.elements[1]
		<< ">";
	return os;
}

vec2 operator+(const vec2& u, const vec2& v) {
	return { _mm_add_ps(u.chunk, v.chunk) };
}

vec2 operator-(const vec2& u, const vec2& v) {
	return { _mm_sub_ps(u.chunk, v.chunk) };
}

vec2 operator*(const float& a, const vec2& v) {
	return { _mm_mul_ps(_mm_set1_ps(a), v.chunk) };
}

vec2 operator*(const vec2& v, const float& a) {
	return { _mm_mul_ps(_mm_set1_ps(a), v.chunk) };
}

float dot(const vec2& u, const vec2& v) {
	return u.elements[0] * v.elements[0] \
		+ u.elements[1] * v.elements[1];
}

float norm(const vec2& u) {
	return sqrtf(dot(u, u));
}

vec2 normalize(const vec2& u) {
	return (1.0f / sqrtf(dot(u, u))) * u;
}

vec2 project(const vec2& u, const vec2& v) {
	vec2 basis = normalize(v);
	return dot(u, basis) * basis;
}

vec2 reject(const vec2& u, const vec2& v) {
	return u - project(u, v);
}
#pragma endregion
//-------------------    Vec3    ---------------------------//
#pragma region

std::ostream& operator<<(std::ostream& os, const vec3& vector) {
	os << "<"
		<< vector.elements[0]
		<< ", " << vector.elements[1]
		<< ", " << vector.elements[2]
		<< ">";
	return os;
}

vec3 operator+(const vec3& u, const vec3& v) {
	return { _mm_add_ps(u.chunk, v.chunk) };
}

vec3 operator-(const vec3& u, const vec3& v) {
	return { _mm_sub_ps(u.chunk, v.chunk) };
}

vec3 operator*(const float& a, const vec3& v) {
	return { _mm_mul_ps(_mm_set1_ps(a), v.chunk) };
}

vec3 operator*(const vec3& v, const float& a) {
	return { _mm_mul_ps(_mm_set1_ps(a), v.chunk) };
}

float dot(const vec3& u, const vec3& v) {
	return u.elements[0] * v.elements[0] \
		+ u.elements[1] * v.elements[1]
		+ u.elements[2] * v.elements[2];
}

float norm(const vec3& u) {
	return sqrtf(dot(u, u));
}

vec3 normalize(const vec3& u) {
	return (1.0f / sqrtf(dot(u, u))) * u;
}

vec3 project(const vec3& u, const vec3& v) {
	vec3 basis = normalize(v);
	return dot(u, basis) * basis;
}

vec3 reject(const vec3& u, const vec3& v) {
	return u - project(u, v);
}

vec3 cross(const vec3& u, const vec3& v) {
	return {
		u.elements[1] * v.elements[2] - u.elements[2] * v.elements[1],
		u.elements[2] * v.elements[0] - u.elements[0] * v.elements[2],
		u.elements[0] * v.elements[1] - u.elements[1] * v.elements[0],
		0.0f };
}
#pragma endregion
//-------------------    Vec4    ---------------------------//
#pragma region

std::ostream& operator<<(std::ostream& os, const vec4& vector) {
	os << "<"
		<< vector.elements[0]
		<< ", " << vector.elements[1]
		<< ", " << vector.elements[2]
		<< ", " << vector.elements[3]
		<< ">";
	return os;
}

vec4 operator+(const vec4& u, const vec4& v) {
	return { _mm_add_ps(u.chunk, v.chunk) };
}

vec4 operator-(const vec4& u, const vec4& v) {
	return { _mm_sub_ps(u.chunk, v.chunk) };
}

vec4 operator*(const float& a, const vec4& v) {
	return { _mm_mul_ps(_mm_set1_ps(a), v.chunk) };
}

vec4 operator*(const vec4& v, const float& a) {
	return { _mm_mul_ps(_mm_set1_ps(a), v.chunk) };
}

float dot(const vec4& u, const vec4& v) {
	return u.elements[0] * v.elements[0] \
		+ u.elements[1] * v.elements[1]
		+ u.elements[2] * v.elements[2]
		+ u.elements[3] * v.elements[3];
}

float norm(const vec4& u) {
	return sqrtf(dot(u, u));
}

vec4 normalize(const vec4& u) {
	return (1.0f / sqrtf(dot(u, u))) * u;
}

vec4 project(const vec4& u, const vec4& v) {
	vec4 basis = normalize(v);
	return dot(u, basis) * basis;
}

vec4 reject(const vec4& u, const vec4& v) {
	return u - project(u, v);
}
#pragma endregion
//-------------------    Mat4    ---------------------------//
#pragma region

std::ostream& operator<<(std::ostream& os, const mat4& m) {
	for (size_t i = 0; i < 4; ++i) {
		os << "|" << m.elements[i] << " " 
			<< m.elements[i + 4] << " " 
			<< m.elements[i + 8] << " " 
			<< m.elements[i + 12] << "|" << std::endl;
	}
	return os;
}

mat4 operator+(const mat4& m, const mat4& n) {
	return {
		_mm256_add_ps(m.chunk[0], n.chunk[0]),
		_mm256_add_ps(m.chunk[1], n.chunk[1]),
	};
}

mat4 operator-(const mat4& m, const mat4& n) {
	return {
		_mm256_sub_ps(m.chunk[0], n.chunk[0]),
		_mm256_sub_ps(m.chunk[1], n.chunk[1]),
	};
}

mat4 operator*(const float& a, const mat4& m) {
	return {
		_mm256_mul_ps(m.chunk[0], _mm256_set1_ps(a)),
		_mm256_mul_ps(m.chunk[1], _mm256_set1_ps(a)),
	};
}

mat4 operator*(const mat4& m, const float& a) {
	return {
		_mm256_mul_ps(m.chunk[0], _mm256_set1_ps(a)),
		_mm256_mul_ps(m.chunk[1], _mm256_set1_ps(a)),
	};
}

vec4 operator*(const mat4& m, const vec4& v) {
	return {
		_mm_fmadd_ps(
			m.column[0], _mm_set1_ps(v.elements[0]), _mm_fmadd_ps(
				m.column[1], _mm_set1_ps(v.elements[1]), _mm_fmadd_ps(
					m.column[2], _mm_set1_ps(v.elements[2]), _mm_mul_ps(
						m.column[3], _mm_set1_ps(v.elements[3])))))
	};
}

mat4 operator*(const mat4& m, const mat4& n) {
	mat4 result;

	for (size_t j = 0; j < 4; ++j) {
		result.column_vector[j] = m * n.column_vector[j];
	}

	return result;
}

mat4 make_mat4_identity() {

	return {
		1.0f, 0.0f, 0.0f, 0.0f,
		0.0f, 1.0f, 0.0f, 0.0f,
		0.0f, 0.0f, 1.0f, 0.0f,
		0.0f, 0.0f, 0.0f, 1.0f,
	};
}

mat4 make_perspective_projection(const float& fovy, const float& aspect,
	const float& near, const float& far) {

	float t{ tanf(deg2rad(0.5f * fovy)) };

	float A = 1.0f / (t * aspect);
	float B = 1.0f / t;
	float C = far / (far - near);
	float D = -near * far / (far - near);

	return {
		A, 0, 0, 0,
		0, B, 0, 0,
		0, 0, C, 1,
		0, 0, D, 0
	};
}

mat4 make_lookat(const vec3& eye, const vec3& target, const vec3& up) {

	vec3 forwards = normalize(target - eye);
	vec3 right = normalize(cross(forwards, up));
	vec3 local_up = normalize(cross(right, forwards));

	//forwards = -1.0f * forwards;

	return {
		right.elements[0], local_up.elements[0], forwards.elements[0], 0.0f,
		right.elements[1], local_up.elements[1], forwards.elements[1], 0.0f,
		right.elements[2], local_up.elements[2], forwards.elements[2], 0.0f,
		-dot(right, eye), -dot(local_up, eye), -dot(forwards, eye), 1.0f

	};
}

mat4 make_translation(const vec3& v) {

	return {
		1.0f, 0.0f, 0.0f, 0.0f,
		0.0f, 1.0f, 0.0f, 0.0f,
		0.0f, 0.0f, 1.0f, 0.0f,
		v.elements[0], v.elements[1], v.elements[2], 1.0f
	};
}

mat4 make_x_rotation(const float& angle) {

	float theta = deg2rad(angle);
	float cT = cosf(theta);
	float sT = sinf(theta);

	return {
		1.0f, 0.0f, 0.0f, 0.0f,
		0.0f,   cT,  -sT, 0.0f,
		0.0f,   sT,   cT, 0.0f,
		0.0f, 0.0f, 0.0f, 1.0f
	};
}

mat4 make_y_rotation(const float& angle) {

	float theta = deg2rad(angle);
	float cT = cosf(theta);
	float sT = sinf(theta);

	return {
		  cT, 0.0f,   sT, 0.0f,
		0.0f, 1.0f, 0.0f, 0.0f,
		 -sT, 0.0f,   cT, 0.0f,
		0.0f, 0.0f, 0.0f, 1.0f
	};
}

mat4 make_z_rotation(const float& angle) {

	float theta = deg2rad(angle);
	float cT = cosf(theta);
	float sT = sinf(theta);

	return {
		  cT,  -sT, 0.0f, 0.0f,
		  sT,   cT, 0.0f, 0.0f,
		0.0f, 0.0f, 1.0f, 0.0f,
		0.0f, 0.0f, 0.0f, 1.0f
	};
}

mat4 lerp(const mat4& m, const mat4& n, const float& t) {
	return m + t * (n - m);
}

mat4 transpose(const mat4& m) {
	return {
		m.elements[0], m.elements[4],  m.elements[8], m.elements[12],
		m.elements[1], m.elements[5],  m.elements[9], m.elements[13],
		m.elements[2], m.elements[6], m.elements[10], m.elements[14],
		m.elements[3], m.elements[7], m.elements[11], m.elements[15],
	};
}

mat4 fast_inverse(const mat4& m) {

	//Get the scale factors
	float a = sqrtf(dot(m.column_vector[0], m.column_vector[0]));
	float b = sqrtf(dot(m.column_vector[1], m.column_vector[1]));
	float c = sqrtf(dot(m.column_vector[2], m.column_vector[2]));

	//Get the rotation vectors, apply inverse scaling
	vec4 X = (1.0f / a) * normalize(m.column_vector[0]);
	vec4 Y = (1.0f / b) * normalize(m.column_vector[1]);
	vec4 Z = (1.0f / c) * normalize(m.column_vector[2]);
	vec4 T = -1.0f * normalize(m.column_vector[3]);

	return {
		X.elements[0], Y.elements[0], Z.elements[0], 0.0f,
		X.elements[1], Y.elements[1], Z.elements[1], 0.0f,
		X.elements[2], Y.elements[2], Z.elements[2], 0.0f,
		dot(X, T), dot(Y, T), dot(Z, T), 1.0f };
}

mat4 make_scale(const float& s) {
	return {
		   s, 0.0f, 0.0f, 0.0f,
		0.0f,    s, 0.0f, 0.0f,
		0.0f, 0.0f,    s, 0.0f,
		0.0f, 0.0f, 0.0f, 1.0f};
}
#pragma endregion
//----------------------------------------------------------//