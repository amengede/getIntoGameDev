#pragma once
#include "../config.h"
#include <TinyGLTF/stb_image.h>

struct image {
	unsigned char* pixels;
	int width, height, channels;
};

namespace util {
	image load_from_file(const char* filename);

	void free_image_memory(image oldImage);
}