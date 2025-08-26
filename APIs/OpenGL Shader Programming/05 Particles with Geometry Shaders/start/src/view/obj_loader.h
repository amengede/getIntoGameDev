#pragma once
#include "../config.h"

namespace util {

	struct MeshCreateInfo {
		const char* filename;
		glm::mat4 preTransform;
	};

	std::vector<float> load_model_from_file(MeshCreateInfo* createInfo);
	std::vector<float> load_toon_model_from_file(MeshCreateInfo* createInfo);
	std::vector<std::string> split(std::string line, std::string delimiter);
	std::map<std::string, glm::vec3> read_mtl_file(std::string filepath);
	std::vector<float> build_face(
		const std::vector<std::string>& description, const std::vector<glm::vec3>& vertices,
		glm::vec3 color, const std::vector<glm::vec3>& normals, int position_offset, int normal_offset
	);
}