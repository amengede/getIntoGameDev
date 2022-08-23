#pragma once
#include "../config.h"
#include "ray.h"
#include "sphere.h"

class Box3D {

public:
	std::array<glm::vec3,2> bounds;

	Box3D(glm::vec3 minCorner, glm::vec3 maxCorner) {
		bounds[0] = minCorner;
		bounds[1] = maxCorner;
	}

	bool overlapsWith(Sphere* sphere) {

		if ((sphere->center.x - sphere->radius) > bounds[1].x) {
			return false;
		}
		if ((sphere->center.x + sphere->radius) < bounds[0].x) {
			return false;
		}
		if ((sphere->center.y - sphere->radius) > bounds[1].y) {
			return false;
		}
		if ((sphere->center.y + sphere->radius) < bounds[0].y) {
			return false;
		}
		if ((sphere->center.z - sphere->radius) > bounds[1].z) {
			return false;
		}
		if ((sphere->center.z + sphere->radius) < bounds[0].z) {
			return false;
		}
		return true;
	}

	bool hit(const Ray& ray) {

		/*
		* from: https://www.scratchapixel.com/lessons/3d-basic-rendering/minimal-ray-tracer-rendering-simple-shapes/ray-box-intersection
		*/

		float tmin, tmax, tymin, tymax, tzmin, tzmax;

		//Get the t value to hit along the x axis
		tmin = (bounds[ray.sign[0]].x - ray.origin.x) * ray.invDir.x;
		tmax = (bounds[1 - ray.sign[0]].x - ray.origin.x) * ray.invDir.x;

		//Get the t value to hit along the y axis
		tymin = (bounds[ray.sign[1]].y - ray.origin.y) * ray.invDir.y;
		tymax = (bounds[1 - ray.sign[1]].y - ray.origin.y) * ray.invDir.y;

		//The each of the mins should be less than each of the maxes,
		//if this is violated, the ray didn't hit.
		if ((tmin > tymax) || (tymin > tmax)) {
			return false;
		}

		//update new bounds
		if (tymin > tmin) {
			tmin = tymin;
		}

		if (tymax < tmax) {
			tmax = tymax;
		}

		//Get the t value to hit along the z axis
		tzmin = (bounds[ray.sign[2]].z - ray.origin.z) * ray.invDir.z;
		tzmax = (bounds[1 - ray.sign[2]].z - ray.origin.z) * ray.invDir.z;

		//The each of the mins should be less than each of the maxes,
		//if this is violated, the ray didn't hit.
		if ((tmin > tzmax) || (tzmin > tmax)) {
			return false;
		}

		return true;
	}
};