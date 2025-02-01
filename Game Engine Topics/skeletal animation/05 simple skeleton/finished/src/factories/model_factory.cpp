#include "model_factory.h"
#include "../stb_image.h"

StaticMesh MeshFactory::make_skeleton() {

    StaticMesh mesh;
    
    std::vector<Vertex> vertices = { {
        {glm::vec3(0.0f), 0},
        {glm::vec3(0.0f, -0.5f, 0.0f), 1},
        {glm::vec3(0.0f, -1.0f, 0.0f), 3},
        {glm::vec3(0.0f, -0.5f, 0.0f), 2},
        {glm::vec3(0.0f, -1.0f, 0.0f), 4},
    } };

    std::vector<uint16_t> indices = { { 0, 1, 1, 2, 0, 3, 3, 4} };

    glGenVertexArrays(1, &mesh.VAO);
    glBindVertexArray(mesh.VAO);

    glGenBuffers(1, &mesh.VBO);
    glBindBuffer(GL_ARRAY_BUFFER, mesh.VBO);
    glBufferData(GL_ARRAY_BUFFER, vertices.size() * sizeof(Vertex),
        vertices.data(), GL_STATIC_DRAW);

    glGenBuffers(1, &mesh.EBO);
    glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, mesh.EBO);
    glBufferData(GL_ELEMENT_ARRAY_BUFFER,
        indices.size() * sizeof(uint16_t),
        indices.data(), GL_STATIC_DRAW);
    mesh.elementCount = indices.size();

    //position
    glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, 16, (void*)0);
    glEnableVertexAttribArray(0);
    //bone
    glVertexAttribIPointer(1, 1, GL_UNSIGNED_INT, 16, (void*)12);
    glEnableVertexAttribArray(1);

    return mesh;
}