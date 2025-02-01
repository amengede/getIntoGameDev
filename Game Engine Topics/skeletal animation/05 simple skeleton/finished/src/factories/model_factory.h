#pragma once
#include "../config.h"

struct StaticMesh {
    unsigned int elementCount, VAO, VBO, EBO;
};

struct Vertex {
    glm::vec3 pos;
    //Simplification: each point will just be controlled by one bone.
    unsigned int bone;
};

class MeshFactory {

public:

    StaticMesh make_skeleton();

};