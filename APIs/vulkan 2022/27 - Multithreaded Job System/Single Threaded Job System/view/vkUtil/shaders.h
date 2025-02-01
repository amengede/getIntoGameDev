#pragma once
#include "../../config.h"

namespace vkUtil {

	/**
		Read a file.

		\param filename a string representing the path to the file
		\returns the contents as a vector of raw binary characters
	*/
	std::vector<char> readFile(std::string filename);

	/**
		Make a shader module.

		\param filename a string holding the filepath to the spir-v file.
		\param device the logical device
		\returns the created shader module
	*/
	vk::ShaderModule createModule(std::string filename, vk::Device device);
}