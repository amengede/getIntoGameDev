#pragma once
#include "../config.h"
#include "box.h"
#include "sphere.h"

class Node {
public:
	bool isInternal;
	Box3D* volume;
	std::array<Node*, 8> children;
	std::vector<Sphere*> spheres;
	int maxSpheres;


	Node(Box3D* volume) {
		this->volume = volume;

		for (int i = 0; i < 8; ++i) {
			children[i] = nullptr;
		}

		this->isInternal = false;
		maxSpheres = 16;
	}

	~Node() {
		delete volume;

		for (int i = 0; i < 8; ++i) {
			if (children[i]) {
				delete children[i];
			}
		}
	}
};