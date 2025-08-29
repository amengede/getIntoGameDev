#include "material.h"
#include "image.h"
#include <glad/glad.h>

Material::Material(MaterialCreateInfo* createInfo) {
	int texWidth, texHeight;
	image material = util::load_from_file(createInfo->filename);
	texWidth = material.width;
	texHeight = material.height;
	unsigned char* data = material.pixels;
	glGenTextures(1, &texture);
	glBindTexture(GL_TEXTURE_2D, texture);
	glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA8, texWidth, texHeight,
				 0, GL_RGBA, GL_UNSIGNED_BYTE, data);
	glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_REPEAT);
	glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_REPEAT);
	glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR_MIPMAP_LINEAR);
	glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR);
	util::free_image_memory(material);
}

Material::~Material() {
	glDeleteTextures(1, &texture);
}
void Material::use() {
	glActiveTexture(GL_TEXTURE0);
	glBindTexture(GL_TEXTURE_2D, texture);
}
