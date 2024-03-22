#include "model_factory.h"
#include "../stb_image.h"
#include <glad/glad.h>
#include <glm/gtc/matrix_transform.hpp>
#include <fstream>
#include <iostream>

Mesh MeshFactory::make_mesh(int i) {

    Mesh mesh;

    reset();

    read_mtl(mtlNames[i], mesh);

    read_obj(objNames[i], i);

    glGenVertexArrays(1, &mesh.VAO);
    glBindVertexArray(mesh.VAO);

    glGenBuffers(1, &mesh.VBO);
    glBindBuffer(GL_ARRAY_BUFFER, mesh.VBO);
    glBufferData(GL_ARRAY_BUFFER, vertices.size() * sizeof(float),
        vertices.data(), GL_STATIC_DRAW);
    //position
    glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, 36, (void*)0);
    glEnableVertexAttribArray(0);
    //texture coordinates
    glVertexAttribPointer(1, 3, GL_FLOAT, GL_FALSE, 36, (void*)12);
    glEnableVertexAttribArray(1);
    //normal
    glVertexAttribPointer(2, 3, GL_FLOAT, GL_FALSE, 36, (void*)24);
    glEnableVertexAttribArray(2);

    glGenBuffers(1, &mesh.EBO);
    glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, mesh.EBO);
    glBufferData(GL_ELEMENT_ARRAY_BUFFER,
        indices.size() * sizeof(uint32_t),
        indices.data(), GL_STATIC_DRAW);


    mesh.elementCount = indices.size();

    return mesh;
}

void MeshFactory::reset() {
    v.clear();
    vt.clear();
    vn.clear();
    history.clear();
    indices.clear();
    material_indices.clear();
    material_filenames.clear();
}

void MeshFactory::read_mtl(const char* filename, Mesh& mesh) {

    //std::cout << "load " << filename << std::endl;

    std::string line;
    std::vector<std::string> words;

    std::ifstream file;

    int materialCount = 0;

    file.open(filename);
    while (std::getline(file, line)) {

        words = split(line, " ");

        if (!words[0].compare("newmtl")) {
            current_material = words[1];
        }

        else if (!words[0].compare("map_Kd")) {
            material_filenames[current_material] = words[1];
            material_indices[current_material] = materialCount++;
        }
    }
    file.close();

    load_materials(mesh, materialCount);

    //std::cout << "successful" << std::endl;
}

void MeshFactory::load_materials(Mesh& mesh, int materialCount) {

    //std::cout << "there are " << materialCount << " materials to load." << std::endl;

    glGenTextures(1, &mesh.material);
    glBindTexture(GL_TEXTURE_2D_ARRAY, mesh.material);
    glTexStorage3D(GL_TEXTURE_2D_ARRAY, 1, GL_RGBA8, 1024, 1024, materialCount);

    for (auto& item : material_indices) {
        //std::cout << static_cast<int>(item.second) << " load " << material_filenames[item.first] << std::endl;
        int width, height, channels;
        stbi_set_flip_vertically_on_load(true);
        unsigned char* data = stbi_load(material_filenames[item.first].c_str(), &width, &height, &channels, STBI_rgb_alpha);
        //std::cout << "Width: " << width << ", Height: " << height << ", channels: " << channels << std::endl;
        //std::cout << &data << std::endl;

        glTexSubImage3D(GL_TEXTURE_2D_ARRAY, 0,
            0, 0, static_cast<int>(item.second),
            width, height, 1,
            GL_RGBA, GL_UNSIGNED_BYTE, data);
        //std::cout << "successful 1" << std::endl;

        //free data
        stbi_image_free(data);
        //std::cout << "successful 2" << std::endl;
    }

    //Configure sampler
    glTexParameteri(GL_TEXTURE_2D_ARRAY, GL_TEXTURE_WRAP_S, GL_REPEAT);
    glTexParameteri(GL_TEXTURE_2D_ARRAY, GL_TEXTURE_WRAP_T, GL_REPEAT);
    glTexParameteri(GL_TEXTURE_2D_ARRAY, GL_TEXTURE_WRAP_R, GL_REPEAT);
    glTexParameteri(GL_TEXTURE_2D_ARRAY, GL_TEXTURE_MIN_FILTER, GL_NEAREST);
    glTexParameteri(GL_TEXTURE_2D_ARRAY, GL_TEXTURE_MAG_FILTER, GL_LINEAR);
}

void MeshFactory::read_obj(const char* filename, int i) {
    //std::cout << "load " << filename << std::endl;
    std::string line;
    std::vector<std::string> words;

    std::ifstream file;

    file.open(filename);

    while (std::getline(file, line)) {

        //std::cout << line << std::endl;

        words = split(line, " ");

        if (!words[0].compare("v")) {
            v.push_back(read_vec3(words, scales[i]));
        }

        else if (!words[0].compare("vt")) {
            vt.push_back(read_vec2(words));
        }

        else if (!words[0].compare("vn")) {
            vn.push_back(read_vec3(words, 1.0f));
        }

        else if (!words[0].compare("usemtl")) {
            current_material = words[1];
        }

        else if (!words[0].compare("f")) {
            read_face(words);
        }
    }
    file.close();
    //std::cout << "loaded " << filename << std::endl;
}

glm::vec3 MeshFactory::read_vec3(std::vector<std::string> words, float preScale) {
    return preScale * glm::vec3(std::stof(words[1]), std::stof(words[2]), std::stof(words[3]));
}

glm::vec2 MeshFactory::read_vec2(std::vector<std::string> words) {
    return glm::vec2(std::stof(words[1]), std::stof(words[2]));
}

void MeshFactory::read_face(std::vector<std::string> words) {

    size_t triangleCount = words.size() - 3;

    for (size_t i = 0; i < triangleCount; ++i) {
        read_corner(words[1]);
        read_corner(words[2 + i]);
        read_corner(words[3 + i]);
    }

}

void MeshFactory::read_corner(std::string description) {
    if (!history.contains(description)) {
        history[description] = static_cast<uint32_t>(vertices.size() / 9);

        std::vector<std::string> attribute_indices = split(description, "/");

        //access attributes
        for (int attr = 0; attr < attribute_indices.size(); ++attr) {
            //position
            glm::vec3 pos = v[std::stol(attribute_indices[0]) - 1];
            vertices.push_back(pos[0]);
            vertices.push_back(pos[1]);
            vertices.push_back(pos[2]);

            //tex coord
            glm::vec2 texcoord = vt[std::stol(attribute_indices[1]) - 1];
            vertices.push_back(texcoord[0]);
            vertices.push_back(texcoord[1]);
            vertices.push_back(material_indices[current_material]);

            //normal
            glm::vec3 normal = vn[std::stol(attribute_indices[2]) - 1];
            vertices.push_back(normal[0]);
            vertices.push_back(normal[1]);
            vertices.push_back(normal[2]);
        }
    }

    indices.push_back(history[description]);
}