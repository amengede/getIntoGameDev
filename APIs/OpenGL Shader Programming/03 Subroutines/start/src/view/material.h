#pragma once

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
