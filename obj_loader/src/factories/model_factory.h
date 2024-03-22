#pragma once
#include "../config.h"

class MeshFactory {

public:

    Mesh make_mesh(int i);

private:

    void reset();

    void read_mtl(const char* filename, Mesh& mesh);

    void load_materials(Mesh& mesh, int materialCount);

    void read_obj(const char* filename, int i);

    glm::vec3 read_vec3(std::vector<std::string> words, float preScale);

    glm::vec2 read_vec2(std::vector<std::string> words);

    void read_face(std::vector<std::string> words);

    void read_corner(std::string description);

    std::vector<glm::vec3> v, vn;
    std::vector<glm::vec2> vt;
    std::unordered_map<std::string, uint32_t> history;
    std::vector<float> vertices;
    std::vector<uint32_t> indices;
    std::unordered_map<std::string, float> material_indices;
    std::unordered_map<std::string, std::string> material_filenames;
    std::string current_material;

};