#pragma once
#include "../config.h"
#include "ray.h"

struct hit_record {
	glm::vec3 point;
	glm::vec3 normal;
	glm::vec3 color;
	float t;

	bool front_face;

	inline void set_face_normal(const Ray& ray, const glm::vec3& outward_normal) {
		front_face = glm::dot(ray.direction, outward_normal) < 0;
		normal = front_face ? outward_normal : -outward_normal;
	}
};