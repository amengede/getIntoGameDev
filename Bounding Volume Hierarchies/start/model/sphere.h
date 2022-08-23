#pragma once
#include "../config.h"
#include "ray.h"
#include "hit_record.h"

struct SphereCreateInfo {
	glm::vec3 center, color;
	float radius;
};

class Sphere {
public:
	glm::vec3 center, color;
	float radius;

	Sphere(SphereCreateInfo* createInfo);
	bool hit(const Ray& ray, float t_min, float t_max, hit_record& rec);

};