#pragma once
#include "../config.h"
#include "image.h"

struct MaterialCreateInfo {
	const char* filename;
};

class Material {
public:

	unsigned int texture;
	
	Material(MaterialCreateInfo* createInfo);
	~Material();
	void use();
};