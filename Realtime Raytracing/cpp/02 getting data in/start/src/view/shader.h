#pragma once
#include "../config.h"

unsigned int make_module(const std::string& filepath, unsigned int module_type);

unsigned int make_shader(
    const std::string& vertex_filepath, const std::string& fragment_filepath);

unsigned int make_compute_shader(const std::string& filepath);