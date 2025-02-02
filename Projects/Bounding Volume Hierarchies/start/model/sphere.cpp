#include "sphere.h"

Sphere::Sphere(SphereCreateInfo* createInfo) {

	this->center = createInfo->center;
	this->color = createInfo->color;
	this->radius = createInfo->radius;

}

bool Sphere::hit(const Ray& ray, float t_min, float t_max, hit_record& rec) {

	glm::vec3 oc = ray.origin - center;
	float a = glm::dot(ray.direction, ray.direction);
	float b = 2.0 * glm::dot(oc, ray.direction);
	float c = dot(oc, oc) - radius * radius;
	float discriminant = b * b - 4.0f * a * c;

	if (discriminant < 0) {
		return false;
	}
	
	float root{ (-b - glm::sqrt(discriminant)) / (2.0f * a) };
	if (root < t_min || t_max < root) {
		return false;
	}

	rec.t = root;
	rec.point = ray.origin + root * ray.direction;
	//rec.normal = (rec.point - center)/radius;
	rec.set_face_normal(ray, (rec.point - center) / radius);
	rec.color = color;

	return true;
}