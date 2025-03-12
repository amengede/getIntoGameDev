#pragma once
#include <intrin.h>
#include <math.h>
#include <iostream>

//-------------------    Vec2    ---------------------------//
#pragma region
struct vec2 {
	union {
		__m128 chunk;
		float elements[4];
	};
};

std::ostream& operator<<(std::ostream& os, const vec2& vector);

vec2 operator+(const vec2& u, const vec2& v);

vec2 operator-(const vec2& u, const vec2& v);

vec2 operator*(const float& a, const vec2& v);

vec2 operator*(const vec2& v, const float& a);

float dot(const vec2& u, const vec2& v);

float norm(const vec2& u);

vec2 normalize(const vec2& u);

vec2 project(const vec2& u, const vec2& v);

vec2 reject(const vec2& u, const vec2& v);
#pragma endregion
//-------------------    Vec3    ---------------------------//
#pragma region
struct vec3 {
	union {
		__m128 chunk;
		float elements[4];
	};
};

std::ostream& operator<<(std::ostream& os, const vec3& vector);

vec3 operator+(const vec3& u, const vec3& v);

vec3 operator-(const vec3& u, const vec3& v);

vec3 operator*(const float& a, const vec3& v);

vec3 operator*(const vec3& v, const float& a);

float dot(const vec3& u, const vec3& v);

float norm(const vec3& u);

vec3 normalize(const vec3& u);

vec3 project(const vec3& u, const vec3& v);

vec3 reject(const vec3& u, const vec3& v);

vec3 cross(const vec3& u, const vec3& v);
#pragma endregion
//-------------------    Vec4    ---------------------------//
#pragma region
struct vec4 {
	union {
		__m128 chunk;
		float elements[4];
	};
};

std::ostream& operator<<(std::ostream& os, const vec4& vector);

vec4 operator+(const vec4& u, const vec4& v);

vec4 operator-(const vec4& u, const vec4& v);

vec4 operator*(const float& a, const vec4& v);

vec4 operator*(const vec4& v, const float& a);

float dot(const vec4& u, const vec4& v);

float norm(const vec4& u);

vec4 normalize(const vec4& u);

vec4 project(const vec4& u, const vec4& v);

vec4 reject(const vec4& u, const vec4& v);
#pragma endregion
//-------------------    Mat4    ---------------------------//
#pragma region
struct mat4 {
	union {
		__m256 chunk[2];
		__m128 column[4];
		vec4 column_vector[4];
		float elements[16];
	};
};

std::ostream& operator<<(std::ostream& os, const mat4& m);

mat4 operator+(const mat4& m, const mat4& n);

mat4 operator-(const mat4& m, const mat4& n);

mat4 operator*(const float& a, const mat4& m);

mat4 operator*(const mat4& m, const float& a);

vec4 operator*(const mat4& m, const vec4& v);

mat4 operator*(const mat4& m, const mat4& n);

/**
 *	@returns a new 4x4 matrix storing the identity transform.
*/
mat4 make_mat4_identity();

/**
 * @brief Make a perspective projection matrix.
 *
 * @param fovy the field of view angle of the frustrum (in degrees)
 * @param aspect the aspect ratio width/height
 * @param near the near view distance of the frustrum
 * @param far the far distance of the frustrum
 * 
 * @returns a new mat4 representing the perspective projection transform
*/
mat4 make_perspective_projection(const float& fovy, const float& aspect,
	const float& near, const float& far);

/**
 * @brief Make a view matrix (translates and rotates the world around the
 * given reference point)
 *
 * @param eye the position of the viewer
 * @param target the position the viewer is looking at
 * @param up the up direction from the viewer's point of reference
 *
 * @returns a new mat4 representing the view transform
*/
mat4 make_lookat(const vec3& eye, const vec3& target, const vec3& up);

/**
 * @brief Make a translation transform matrix.
 *
 * @param v the displacement to apply
 *
 * @returns a new mat4 representing the transform
*/
mat4 make_translation(const vec3& v);

/**
 * @brief Make a rotation around the x-axis.
 *
 * @param angle the angle to rotate by (in degrees)
 * 
 * @returns a new mat4 representing the transform
*/
mat4 make_x_rotation(const float& angle);

/**
 * @brief Make a rotation around the y-axis.
 *
 * @param angle the angle to rotate by (in degrees)
 * 
 * @returns a new mat4 representing the transform
*/
mat4 make_y_rotation(const float& angle);

/**
 * @brief Make a rotation around the z-axis.
 *
 * @param angle the angle to rotate by (in degrees)
 * 
 * @returns a new mat4 representing the transform
*/
mat4 make_z_rotation(const float& angle);

/**
 * @brief Blend (linearly interpolate) two matrices.
 *
 * @param m the start matrix (t = 0)
 * @param n the end matrix (t = 1)
 * @param t the interpolation parameter
 *
 * @returns the result m3 = m + t * (n - m)
*/
mat4 lerp(const mat4& m, const mat4& n, const float& t);

/**
 * @returns a transposed copy of the given matrix
*/
mat4 transpose(const mat4& m);

/**
 * @brief Compute a fast transform matrix inverse.
 *
 * @param matrix the m to invert
 * 
 * @returns the inverse
*/
mat4 fast_inverse(const mat4& m);

/**
* @returns a scale transform
*/
mat4 make_scale(const float& s);
#pragma endregion
//----------------------------------------------------------//