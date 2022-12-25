#pragma once
#include "config.h"

namespace vkUtil {

	/**
		Read a file.

		\param filename a string representing the path to the file
		\param debug whether the system is running in debug mode
		\returns the contents as a vector of raw binary characters
	*/
	std::vector<char> readFile(std::string filename, bool debug) {
		
		std::ifstream file(filename, std::ios::ate | std::ios::binary);

		if (debug && !file.is_open()) {
			std::cout << "Failed to load \"" << filename << "\"" << std::endl;
		}

		size_t filesize{ static_cast<size_t>(file.tellg()) };

		std::vector<char> buffer(filesize);
		file.seekg(0);
		file.read(buffer.data(), filesize);

		file.close();
		return buffer;
	}
}