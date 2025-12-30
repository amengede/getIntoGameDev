#include "image.h"
#define STB_IMAGE_IMPLEMENTATION
#include "stb_image.h"

image util::load_from_file(const char* filename) {
	image result;

	result.pixels = stbi_load(
		filename, &(result.width), &(result.height), &(result.channels), STBI_rgb_alpha
	);

	return result;
}

void util::free_image_memory(image oldImage) {
	stbi_image_free(oldImage.pixels);
}
