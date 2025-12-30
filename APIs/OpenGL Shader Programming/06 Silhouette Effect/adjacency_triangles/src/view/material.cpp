#include "material.h"

Material::Material(MaterialCreateInfo* createInfo) {
	int texWidth, texHeight;
	image material = util::load_from_file(createInfo->filename);
	texWidth = material.width;
	texHeight = material.height;
	unsigned char* data = material.pixels;
	glCreateTextures(GL_TEXTURE_2D, 1, &texture);
	glTextureStorage2D(texture, 1, GL_RGBA8, texWidth, texHeight);
	glTextureSubImage2D(texture, 0, 0, 0, texWidth, texHeight, GL_RGBA, GL_UNSIGNED_BYTE, data);
	glTextureParameteri(texture, GL_TEXTURE_WRAP_S, GL_REPEAT);
	glTextureParameteri(texture, GL_TEXTURE_WRAP_T, GL_REPEAT);
	glTextureParameteri(texture, GL_TEXTURE_MIN_FILTER, GL_LINEAR_MIPMAP_LINEAR);
	glTextureParameteri(texture, GL_TEXTURE_MAG_FILTER, GL_LINEAR);
	util::free_image_memory(material);
}

Material::~Material() {
	glDeleteTextures(1, &texture);
}
void Material::use() {
	glBindTextureUnit(0, texture);
}