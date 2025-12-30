#pragma once
#include "../config.h"

namespace util {

	struct Vertex {
		glm::vec3 pos;
		glm::vec2 texCoord;
		glm::vec3 normal;

		bool operator==(const Vertex& other) const {
			return pos == other.pos && normal == other.normal && texCoord == other.texCoord;
		}
	};

	struct ToonVertex {
		glm::vec3 pos;
		glm::vec3 color;
		glm::vec3 normal;

		bool operator==(const ToonVertex& other) const {
			return pos == other.pos && normal == other.normal && color == other.color;
		}
	};

	struct MeshCreateInfo {
		const char* filename;
		glm::mat4 preTransform;
	};

	struct ModelData {
		std::vector<Vertex> vertices;
		std::vector<ToonVertex> toonVertices;
		std::vector<unsigned int> indices;
	};

	ModelData load_model_from_file(MeshCreateInfo* createInfo);
	ModelData load_toon_model_from_file(MeshCreateInfo* createInfo);
	std::vector<std::string> split(std::string line, std::string delimiter);
	std::map<std::string, glm::vec3> read_mtl_file(std::string filepath);
	void build_face(
		const std::vector<std::string>& description, const std::vector<glm::vec3>& vertices,
		glm::vec3 color, const std::vector<glm::vec3>& normals, int position_offset, int normal_offset,
		ModelData* modelData, std::unordered_map<ToonVertex, uint32_t>* uniqueVertices
	);
}