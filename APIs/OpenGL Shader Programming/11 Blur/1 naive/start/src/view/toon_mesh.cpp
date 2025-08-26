#include "toon_mesh.h"

ToonMesh::ToonMesh(util::MeshCreateInfo* createInfo) {

	std::ifstream parsed_file;

	parsed_file.open(createInfo->parsed_filename, std::ifstream::in);
	if (parsed_file.good()) {
		readParsedModel(parsed_file);
	}
	else {
		std::cout << "Fallback to file parsing.\n";
		unpackData(
			util::load_toon_model_from_file(createInfo)
		);
		writeParsedModel(createInfo->parsed_filename);
	}
	elementCount = static_cast<uint32_t>(indices.size());
	glCreateBuffers(1, &VBO);
	glCreateBuffers(1, &EBO);
	glCreateVertexArrays(1, &VAO);
	glVertexArrayVertexBuffer(VAO, 0, VBO, 0, 9 * sizeof(float));
	glNamedBufferStorage(
		VBO, vertices.size() * sizeof(float), vertices.data(), GL_DYNAMIC_STORAGE_BIT
	);
	glVertexArrayElementBuffer(VAO, EBO);
	glNamedBufferStorage(
		EBO, indices.size() * sizeof(uint32_t), indices.data(), GL_DYNAMIC_STORAGE_BIT
	);
	//pos: 0, color: 1, normal: 2
	glEnableVertexArrayAttrib(VAO, 0);
	glEnableVertexArrayAttrib(VAO, 1);
	glEnableVertexArrayAttrib(VAO, 2);
	glVertexArrayAttribFormat(VAO, 0, 3, GL_FLOAT, GL_FALSE, 0);
	glVertexArrayAttribFormat(VAO, 1, 3, GL_FLOAT, GL_FALSE, 3 * sizeof(float));
	glVertexArrayAttribFormat(VAO, 2, 3, GL_FLOAT, GL_FALSE, 6 * sizeof(float));
	glVertexArrayAttribBinding(VAO, 0, 0);
	glVertexArrayAttribBinding(VAO, 1, 0);
	glVertexArrayAttribBinding(VAO, 2, 0);
}

void ToonMesh::readParsedModel(std::ifstream& file) {

	int writeMode = 0; //0: vertices, 1: indices

	std::string line;

	while (std::getline(file, line)) {
		if (line[0] == 'v') {
			writeMode = 0;
		}
		else if (line[0] == 'i') {
			writeMode = 1;
		}
		else {
			float attribute = strtof(line.c_str(), NULL);
			if (writeMode == 0) {
				vertices.push_back(attribute);
			}
			else {
				indices.push_back(attribute);
			}
		}
	}

	file.close();
}

void ToonMesh::writeParsedModel(const char* filename) {

	std::ofstream file;

	file.open(filename, std::ofstream::out);

	file << "vertices\n";

	for (float attribute : vertices) {
		file << attribute << "\n";
	}

	file << "indices\n";

	for (float attribute : indices) {
		file << attribute << "\n";
	}

	file.close();
}

void ToonMesh::unpackData(util::ModelData modelData) {

	for (util::ToonVertex vertex : modelData.toonVertices) {
		vertices.push_back(vertex.pos.x);
		vertices.push_back(vertex.pos.y);
		vertices.push_back(vertex.pos.z);
		//std::cout << "pos: (" << vertex.pos.x << ", " << vertex.pos.y << ", " << vertex.pos.z << ")" << std::endl;
		vertices.push_back(vertex.color.x);
		vertices.push_back(vertex.color.y);
		vertices.push_back(vertex.color.z);
		//std::cout << "normal: (" << vertex.color.x << ", " << vertex.color.y << ", " << vertex.color.z << ")" << std::endl;
		vertices.push_back(vertex.normal.x);
		vertices.push_back(vertex.normal.y);
		vertices.push_back(vertex.normal.z);
		//std::cout << "normal: (" << vertex.normal.x << ", " << vertex.normal.y << ", " << vertex.normal.z << ")" << std::endl;
	}

	constructAdjacency(modelData);
}

void ToonMesh::constructAdjacency(util::ModelData modelData) {

	unsigned int triangleCount = static_cast<unsigned int>(modelData.indices.size() / 3);
	std::vector<util::Triangle> triangles;

	//Build basic triangle info: points a,b,c
	for (unsigned int i = 0; i < triangleCount; ++i) {

		util::Triangle triangle;
		triangle.index_a = modelData.indices[3 * i];
		triangle.point_a = modelData.toonVertices[triangle.index_a].pos;
		triangle.index_b = modelData.indices[3 * i + 1];
		triangle.point_b = modelData.toonVertices[triangle.index_b].pos;
		triangle.index_c = modelData.indices[3 * i + 2];
		triangle.point_c = modelData.toonVertices[triangle.index_c].pos;
		triangle.connection_ab = NULL;
		triangle.connection_bc = NULL;
		triangle.connection_ca = NULL;

		triangles.push_back(triangle);
	}

	//Connect triangles
	for (unsigned int i = 0; i < triangleCount; ++i) {

		util::Triangle* triangle = &triangles[i];
		for (unsigned int j = 0; j < triangleCount; ++j) {

			if (i == j) {
				continue;
			}

			util::Triangle* triangle2 = &triangles[j];

			if (triangle->connection_ab == NULL) {
				//test ab edge of triangle
				
				if (
					(util::connects(triangle->point_a, triangle2->point_a)
					&& util::connects(triangle->point_b, triangle2->point_b))
					|| (util::connects(triangle->point_a, triangle2->point_b)
						&& util::connects(triangle->point_b, triangle2->point_a))
				) {
					std::cout << "connected ab\n";
					triangle->connection_ab = triangle2;
					triangle->index_ab = triangle2->index_c;
				}
				else if (
					(util::connects(triangle->point_a, triangle2->point_a)
					&& util::connects(triangle->point_b, triangle2->point_c))
					|| (util::connects(triangle->point_a, triangle2->point_c)
						&& util::connects(triangle->point_b, triangle2->point_a))
					) {
					std::cout << "connected ab\n";
					triangle->connection_ab = triangle2;
					triangle->index_ab = triangle2->index_b;
				}
				else if (
					(util::connects(triangle->point_a, triangle2->point_b)
					&& util::connects(triangle->point_b, triangle2->point_c))
					|| (util::connects(triangle->point_a, triangle2->point_c)
						&& util::connects(triangle->point_b, triangle2->point_b))
					) {
					std::cout << "connected ab\n";
					triangle->connection_ab = triangle2;
					triangle->index_ab = triangle2->index_a;
				}
			}

			if (triangle->connection_bc == NULL) {
				//test bc edge of triangle

				if (
					(util::connects(triangle->point_b, triangle2->point_a)
						&& util::connects(triangle->point_c, triangle2->point_b))
					|| (util::connects(triangle->point_b, triangle2->point_b)
						&& util::connects(triangle->point_c, triangle2->point_a))
					) {
					std::cout << "connected bc\n";
					triangle->connection_bc = triangle2;
					triangle->index_bc = triangle2->index_c;
				}
				else if (
					(util::connects(triangle->point_b, triangle2->point_a)
						&& util::connects(triangle->point_c, triangle2->point_c))
					|| (util::connects(triangle->point_b, triangle2->point_c)
						&& util::connects(triangle->point_c, triangle2->point_a))
					) {
					std::cout << "connected bc\n";
					triangle->connection_bc = triangle2;
					triangle->index_bc = triangle2->index_b;
				}
				else if (
					(util::connects(triangle->point_b, triangle2->point_b)
						&& util::connects(triangle->point_c, triangle2->point_c))
					|| (util::connects(triangle->point_b, triangle2->point_c)
						&& util::connects(triangle->point_c, triangle2->point_b))
					) {
					std::cout << "connected bc\n";
					triangle->connection_bc = triangle2;
					triangle->index_bc = triangle2->index_a;
				}
			}

			if (triangle->connection_ca == NULL) {
				//test ca edge of triangle

				if (
					(util::connects(triangle->point_c, triangle2->point_a)
						&& util::connects(triangle->point_a, triangle2->point_b))
					|| (util::connects(triangle->point_c, triangle2->point_b)
						&& util::connects(triangle->point_a, triangle2->point_a))
					) {
					std::cout << "connected ca\n";
					triangle->connection_ca = triangle2;
					triangle->index_ca = triangle2->index_c;
				}
				else if (
					(util::connects(triangle->point_c, triangle2->point_a)
						&& util::connects(triangle->point_a, triangle2->point_c))
					|| (util::connects(triangle->point_c, triangle2->point_c)
						&& util::connects(triangle->point_a, triangle2->point_a))
					) {
					std::cout << "connected ca\n";
					triangle->connection_ca = triangle2;
					triangle->index_ca = triangle2->index_b;
				}
				else if (
					(util::connects(triangle->point_c, triangle2->point_b)
						&& util::connects(triangle->point_a, triangle2->point_c))
					|| (util::connects(triangle->point_c, triangle2->point_c)
						&& util::connects(triangle->point_a, triangle2->point_b))
					) {
					std::cout << "connected ca\n";
					triangle->connection_ca = triangle2;
					triangle->index_ca = triangle2->index_a;
				}
			}

			if (
				triangle->connection_ab != NULL
				&& triangle->connection_bc != NULL
				&& triangle->connection_ca != NULL
				) {
				break;
			}
		}
	}

	for (util::Triangle triangle : triangles) {
		indices.push_back(triangle.index_a);
		indices.push_back(triangle.index_ab);
		indices.push_back(triangle.index_b);
		indices.push_back(triangle.index_bc);
		indices.push_back(triangle.index_c);
		indices.push_back(triangle.index_ca);
	}
}

ToonMesh::~ToonMesh() {
	glDeleteBuffers(1, &VBO);
	glDeleteBuffers(1, &EBO);
	glDeleteVertexArrays(1, &VAO);
}