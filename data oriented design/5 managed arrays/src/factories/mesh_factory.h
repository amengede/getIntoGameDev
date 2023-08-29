#pragma once
#include "../config.h"

struct StaticMesh {
    unsigned int VAO, VBO, EBO;
};

class MeshFactory {

public:
    
    void start_obj_mesh();
    void append_obj_mesh(const char* filename, 
        glm::mat4 preTransform, float layer);
    StaticMesh build_obj_mesh();

    unsigned int elementCount;
    unsigned int offset;

private:

    void reserve_space(const char* filename);
    void read_file(const char* filename);
    glm::vec3 read_vec3(std::vector<std::string> words, float w);
    glm::vec2 read_vec2(std::vector<std::string> words);
    void read_face(std::vector<std::string> words);
    void read_corner(std::string description);
    
    std::vector<glm::vec3> v;
    std::vector<glm::vec2> vt;
    std::vector<glm::vec3> vn;
    std::vector<float> vertices;
    std::vector<unsigned int> indices;
    std::unordered_map<std::string, uint32_t> history;

    float current_layer;

    size_t v_loaded, vt_loaded, vn_loaded, last_index;
    size_t last_index_current;

    glm::mat4 preTransform;

};