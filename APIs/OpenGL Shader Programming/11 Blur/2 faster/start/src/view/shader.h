#pragma once

#include "../config.h"

namespace util {

	struct shaderFilePathBundle {
		const char* vertex, *geometry, *tcs, *tes, *fragment;
	};

	unsigned int load_shader(const shaderFilePathBundle& filepaths);
	unsigned int load_shader_module(const char* filepath, unsigned int type);
}