#pragma once
#include "../config.h"

struct StaticMesh {
    unsigned int elementCount, VAO, VBO, EBO, material;
};

struct Vertex {
    glm::vec3 position;
    glm::vec2 texCoord;
    glm::vec3 normal;
};

class MeshFactory {

public:
    
    /*
    * Read a gltf file and construct a model from it.
    * 
    * @param objectName: The name of the object being loaded.
    * @return a fully initialized StaticMesh struct
    */
    StaticMesh build_gltf_mesh(const char* objectName);

private:

    /*
    * Open and read a gltf file.
    *
    * @param filename: The name of the file to open.
    * @return a json value referring to the root of the json object's tree.
    */
    Json::Value read_gltf_file(const char* filename);

    /*
    * Open and read a binary file.
    *
    * @param filename: The name of the file to open.
    * @return a vector containing the raw binary contents of the file.
    */
    std::vector<char> read_binary_file(const char* filename);

    /*
    * Fetch a region of vec3s and write them into a destination
    * vector.
    *
    * @param attributeName: The name of the attribute to fetch.
    * @param gltfData: The root node of the loaded gltf file.
    * @param byteData: The contents of the loaded binary file.
    * @param dst: The destination vector.
    */
    void fetch_vec3(const char* attributeName, 
        Json::Value& gltfData, std::vector<char>& byteData, 
        std::vector<glm::vec3>& dst);

    /*
    * Fetch a region of vec2s and write them into a destination
    * vector.
    *
    * @param attributeName: The name of the attribute to fetch.
    * @param gltfData: The root node of the loaded gltf file.
    * @param byteData: The contents of the loaded binary file.
    * @param dst: The destination vector.
    */
    void fetch_vec2(const char* attributeName,
        Json::Value& gltfData, std::vector<char>& byteData,
        std::vector<glm::vec2>& dst);

    /*
    * Fetch the model indices and write them.
    *
    * @param gltfData: The root node of the loaded gltf file.
    * @param byteData: The contents of the loaded binary file.
    */
    void fetch_indices(Json::Value& gltfData, std::vector<char>& byteData);

    /*
    * Load the model's material and write it to the static mesh
    *
    * @param objectName: The name of the object being loaded.
    * @param gltfData: The root node of the loaded gltf file.
    * @param mesh: The mesh to work on.
    */
    void load_material(const char* objectName, Json::Value& gltfData, StaticMesh& mesh);

    /*
    * "Stitch together" the (presumably populated)
    * v, vt and vn elements to populate a vector
    * of vertices.
    */
    void build_vertices();

    /*
    * Construct and upload to a mesh's buffer objects.
    * After calling this function, describe_attributes
    * should be called.
    *
    * @param mesh: The mesh to work on.
    */
    void build_buffers(StaticMesh& mesh);

    /*
    * Construct attribute pointers in order to describe
    * a mesh's vertex data. This function should be called
    * after build_buffers.
    */
    void describe_attributes();
    
    std::vector<glm::vec3> v;
    std::vector<glm::vec2> vt;
    std::vector<glm::vec3> vn;
    std::vector<Vertex> vertices;
    std::vector<uint16_t> indices;

};