#include "obj_loader.h"
#define TINYOBJLOADER_IMPLEMENTATION
#include "tiny_obj_loader.h"

namespace std {
    template<> struct hash<util::Vertex> {
        size_t operator()(util::Vertex const& vertex) const {
            return ((hash<glm::vec3>()(vertex.pos) ^
                (hash<glm::vec3>()(vertex.normal) << 1)) >> 1) ^
                (hash<glm::vec2>()(vertex.texCoord) << 1);
        }
    };
}

namespace std {
    template<> struct hash<util::ToonVertex> {
        size_t operator()(util::ToonVertex const& vertex) const {
            return ((hash<glm::vec3>()(vertex.pos) ^
                (hash<glm::vec3>()(vertex.normal) << 1)) >> 1) ^
                (hash<glm::vec3>()(vertex.color) << 1);
        }
    };
}

bool util::connects(glm::vec3 point_a, glm::vec3 point_b) {
    return glm::abs(glm::length(point_a - point_b)) < 0.00000001;
}

util::ModelData util::load_model_from_file(MeshCreateInfo* createInfo) {

    util::ModelData modelData;

    tinyobj::attrib_t attributes;
    std::vector<tinyobj::shape_t> shapes;
    std::vector<tinyobj::material_t> materials;
    std::string warning, error;

    std::unordered_map<Vertex, uint32_t> uniqueVertices{};

    if (!tinyobj::LoadObj(&attributes, &shapes, &materials, &warning, &error, createInfo->filename)) {
        std::cout << warning << error << '\n';
    }

    for (const auto& shape : shapes) {
        for (const auto& index : shape.mesh.indices) {

            Vertex vertex{};

            glm::vec4 pos = {
                attributes.vertices[3 * index.vertex_index],
                attributes.vertices[3 * index.vertex_index + 1],
                attributes.vertices[3 * index.vertex_index + 2],
                1
            };

            vertex.pos = glm::vec3(createInfo->preTransform * pos);

            glm::vec3 normal = {
                attributes.normals[3 * index.normal_index],
                attributes.normals[3 * index.normal_index + 1],
                attributes.normals[3 * index.normal_index + 2]
            };

            vertex.normal = glm::normalize(glm::mat3(createInfo->preTransform) * normal);

            vertex.texCoord = {
                attributes.texcoords[2 * index.texcoord_index],
                attributes.texcoords[2 * index.texcoord_index + 1],
            };

            if (uniqueVertices.count(vertex) == 0) {
                uniqueVertices[vertex] = static_cast<uint32_t>(modelData.vertices.size());
                modelData.vertices.push_back(vertex);
            }
            modelData.indices.push_back(uniqueVertices[vertex]);
        }
    }

    return modelData;
}

util::ModelData util::load_toon_model_from_file(MeshCreateInfo* createInfo) {

    util::ModelData modelData{};
    std::unordered_map<ToonVertex, uint32_t> uniqueVertices;

    //raw, unassembled data
    std::vector<glm::vec3> v;
    glm::vec3 color = glm::vec3(1.0);
    std::vector<glm::vec3> vn;
    int position_offset = 1;
    int normal_offset = 1;

    //Material data
    std::map<std::string, glm::vec3> color_lookup;

    //final, assembled and packed result
    std::vector<float> vertices;

    //open the obj file and read the data
    std::ifstream obj_file;
    std::string line;
    obj_file.open(createInfo->filename);
    while (std::getline(obj_file, line)) {

        //split the string
        std::vector<std::string> splitLine = split(line, " ");

        //check flag
        if (splitLine[0].compare("mtllib") == 0) {

            //attempt to open mtl file
            std::stringstream mtl_filepath;
            mtl_filepath << "models/" << splitLine[1];
            color_lookup = read_mtl_file(mtl_filepath.str());
        }
        else if (splitLine[0].compare("o") == 0) {
            //reset object definitions
            position_offset += v.size();
            normal_offset += vn.size();
            v.clear();
            vn.clear();
        }
        else if (splitLine[0].compare("v") == 0) {
            // add a vertex
            glm::vec4 pos = {
                strtof(splitLine[1].c_str(), NULL),
                strtof(splitLine[2].c_str(), NULL),
                strtof(splitLine[3].c_str(), NULL),
                1
            };

            pos = createInfo->preTransform * pos;
            v.push_back(glm::vec3(pos));
        }
        else if (splitLine[0].compare("vn") == 0) {
            // add a normal
            glm::vec3 normal = {
                strtof(splitLine[1].c_str(), NULL),
                strtof(splitLine[2].c_str(), NULL),
                strtof(splitLine[3].c_str(), NULL)
            };

            normal = glm::normalize(glm::mat3(createInfo->preTransform) * normal);
            vn.push_back(normal);
        }
        else if (splitLine[0].compare("usemtl") == 0) {
            //set the color of the "Vertex Paintbrush"
            color = color_lookup[splitLine[1]];
        }
        else if (splitLine[0].compare("f") == 0) {
            //build a face out of the data on the line
            build_face(splitLine, v, color, vn, position_offset, normal_offset, &modelData, &uniqueVertices);
        }
    }
    return modelData;
}

std::vector<std::string> util::split(std::string line, std::string delimiter) {
    std::vector<std::string> splitLine;
    size_t pos = 0;
    while ((pos = line.find(delimiter)) != std::string::npos) {
        splitLine.push_back(line.substr(0, pos));
        line.erase(0, pos + delimiter.length());
    }
    splitLine.push_back(line.substr(0, line.npos));
    return splitLine;
}

std::map<std::string, glm::vec3> util::read_mtl_file(std::string filepath) {

    std::map<std::string, glm::vec3> color_lookup;

    try {
        std::ifstream mtl_file;
        mtl_file.open(filepath.c_str());

        std::string name;

        std::string line;

        while (std::getline(mtl_file, line)) {

            //split the string
            std::vector<std::string> splitLine = split(line, " ");

            //check flag
            if (splitLine[0].compare("newmtl") == 0) {
                //register the name
                name = splitLine[1];
            }
            else if (splitLine[0].compare("Kd") == 0) {
                color_lookup.insert(
                    std::make_pair(
                        name,
                        glm::vec3(
                            strtof(splitLine[1].c_str(), NULL),
                            strtof(splitLine[2].c_str(), NULL),
                            strtof(splitLine[3].c_str(), NULL)
                        )
                    )
                );
            }
        }
    }
    catch (...) {
        color_lookup.insert(std::make_pair("None", glm::vec3(1.0)));
    }

    return color_lookup;
}

void util::build_face(
    const std::vector<std::string>& description, const std::vector<glm::vec3>& vertices,
    glm::vec3 color, const std::vector<glm::vec3>& normals, int position_offset, int normal_offset,
    ModelData* modelData, std::unordered_map<ToonVertex, uint32_t>* uniqueVertices
) {

    std::vector<glm::vec3> faceVertices;
    std::vector<glm::vec3> faceNormals;

    for (int i = 1; i < description.size(); ++i) {
        //std::cout << i;
        //std::cout << description[i] << ", ";

        std::vector<std::string> attributes = split(description[i], "/");
        int position_index = atoi(attributes[0].c_str()) - position_offset;
        faceVertices.push_back(vertices[position_index]);
        int normal_index = atoi(attributes[2].c_str()) - normal_offset;
        faceNormals.push_back(normals[normal_index]);
    }

    // obj file uses triangle fan format for each face individually.
    // unpack each face
    size_t triangle_count = description.size() - 3;

    std::vector<int> vertex_order;
    /*
        eg. 0, 1, 2, 3 unpacks to vertices : [0, 1, 2, 0, 2, 3]
    */

    for (int i = 0; i < triangle_count; ++i) {

        vertex_order.push_back(0);
        vertex_order.push_back(i + 1);
        vertex_order.push_back(i + 2);
    }

    for (int i : vertex_order) {

        util::ToonVertex vertex;

        vertex.pos = faceVertices[i];

        vertex.color = color;

        vertex.normal = faceNormals[i];

        if (uniqueVertices->count(vertex) == 0) {
            (*uniqueVertices)[vertex] = static_cast<uint32_t>(modelData->toonVertices.size());
            modelData->toonVertices.push_back(vertex);
        }
        modelData->indices.push_back((*uniqueVertices)[vertex]);
    }
}