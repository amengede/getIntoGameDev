#define TINYOBJLOADER_IMPLEMENTATION
#include "vk_mesh.h"
#include "../tiny_obj_loader.h"

bool Mesh::loadModel(const char* filename) {
	tinyobj::attrib_t attributes;
	std::vector<tinyobj::shape_t> shapes;
	std::vector<tinyobj::material_t> materials;
	std::string warning, error;

	std::unordered_map<Vertex, uint32_t> uniqueVertices{};
	if (!tinyobj::LoadObj(&attributes, &shapes, &materials, &warning, &error, filename)) {
		throw std::runtime_error(warning + error);
	}

	for (const auto& shape : shapes) {
		for (const auto& index : shape.mesh.indices) {
			Vertex vertex{};

			vertex.pos = {
				attributes.vertices[3 * index.vertex_index],
				attributes.vertices[3 * index.vertex_index + 1],
				attributes.vertices[3 * index.vertex_index + 2]
			};

			vertex.normal = {
				attributes.normals[3 * index.normal_index],
				attributes.normals[3 * index.normal_index + 1],
				attributes.normals[3 * index.normal_index + 2]
			};

			vertex.texCoord = {
				attributes.texcoords[2 * index.texcoord_index],
				attributes.texcoords[2 * index.texcoord_index + 1]
			};

			if (uniqueVertices.count(vertex) == 0) {
				uniqueVertices[vertex] = static_cast<uint32_t>(vertices.size());
				vertices.push_back(vertex);
			}
			indices.push_back(uniqueVertices[vertex]);
		}
	}
}