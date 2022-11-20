#include "gltf_mesh.h"

GLTFStaticMesh::GLTFStaticMesh(const char* filename, float scale) {

    tinygltf::TinyGLTF loader;
    std::string error;
    std::string warning;

    loader.LoadASCIIFromFile(&model, &error, &warning, filename);
    if (!warning.empty()) {
        std::cout << "WARN: " << warning << std::endl;
    }

    if (!error.empty()) {
        std::cout << "ERR: " << error << std::endl;
    }
    VAO_and_EBOs = bindModel();
    this->scale = scale;
}

/*
* Create ebos for the given mesh and register them in the set.
*/
void GLTFStaticMesh::bindMesh(std::map<int, GLuint>& ebos, tinygltf::Mesh& mesh) {

    for (int i = 0; i < model.bufferViews.size(); ++i) {
        const tinygltf::BufferView& bufferView = model.bufferViews[i];
        if (bufferView.target == 0) {
            std::cout << "WARN: bufferView.target is zero" << std::endl;
            continue;  // Unsupported bufferView.
                       /*
                         From spec2.0 readme:
                         https://github.com/KhronosGroup/glTF/tree/master/specification/2.0
                                  ... drawArrays function should be used with a count equal to
                         the count            property of any of the accessors referenced by the
                         attributes            property            (they are all equal for a given
                         primitive).
                       */
        }

        const tinygltf::Buffer& buffer = model.buffers[bufferView.buffer];

        GLuint ebo;
        glGenBuffers(1, &ebo);
        ebos[i] = ebo;
        glBindBuffer(bufferView.target, ebo);

        glBufferData(bufferView.target, bufferView.byteLength,
            &buffer.data.at(0) + bufferView.byteOffset, GL_STATIC_DRAW);
    }

    for (int i = 0; i < mesh.primitives.size(); ++i) {
        tinygltf::Primitive primitive = mesh.primitives[i];
        tinygltf::Accessor indexAccessor = model.accessors[primitive.indices];

        for (auto& attrib : primitive.attributes) {
            tinygltf::Accessor accessor = model.accessors[attrib.second];
            int byteStride =
                accessor.ByteStride(model.bufferViews[accessor.bufferView]);
            glBindBuffer(GL_ARRAY_BUFFER, ebos[accessor.bufferView]);

            int size = 1;
            if (accessor.type != TINYGLTF_TYPE_SCALAR) {
                size = accessor.type;
            }

            int vaa = -1;
            if (attrib.first.compare("POSITION") == 0) vaa = 0;
            if (attrib.first.compare("NORMAL") == 0) vaa = 2;
            if (attrib.first.compare("TEXCOORD_0") == 0) vaa = 1;
            if (vaa > -1) {
                glEnableVertexAttribArray(vaa);
                glVertexAttribPointer(vaa, size, accessor.componentType,
                    accessor.normalized ? GL_TRUE : GL_FALSE,
                    byteStride, ((char*)NULL + accessor.byteOffset));
            }
            else
                std::cout << "vaa missing: " << attrib.first << std::endl;
        }
    }
}

/*
* Inspect a node, create an ebo for its mesh if it has one,
* and recursively check its children
*/
void GLTFStaticMesh::bindModelNodes(std::map<int, GLuint>& ebos, tinygltf::Node& node) {

    if ((node.mesh >= 0) && (node.mesh < model.meshes.size())) {
        //this node holds a mesh, bind it
        bindMesh(ebos, model.meshes[node.mesh]);
    }

    //recursively bind children
    for (int i = 0; i < node.children.size(); i++) {
        assert((node.children[i] >= 0) && (node.children[i] < model.nodes.size()));
        bindModelNodes(ebos, model.nodes[node.children[i]]);
    }
}

/*
* Parse the loaded model data,
* create a vertex array object
* and a set of element buffer objects (Scene might have multiple objects).
*/
std::pair<GLuint, std::map<int, GLuint>> GLTFStaticMesh::bindModel() {
    std::map<int, GLuint> ebos;
    GLuint vao;
    //create the vao
    glGenVertexArrays(1, &vao);
    glBindVertexArray(vao);

    //create an ebo for each node in the scene
    const tinygltf::Scene& scene = model.scenes[model.defaultScene];
    for (size_t i = 0; i < scene.nodes.size(); ++i) {
        assert((scene.nodes[i] >= 0) && (scene.nodes[i] < model.nodes.size()));
        bindModelNodes(ebos, model.nodes[scene.nodes[i]]);
    }

    glBindVertexArray(0);
    //cleanup: make sure only ebos are stored
    for (auto it = ebos.cbegin(); it != ebos.cend();) {
        tinygltf::BufferView bufferView = model.bufferViews[it->first];
        if (bufferView.target != GL_ELEMENT_ARRAY_BUFFER) {
            glDeleteBuffers(1, &ebos[it->first]);
            ebos.erase(it++);
        }
        else {
            ++it;
        }
    }

    return { vao, ebos };
}

/*
* draw each of the primitives in the given mesh
*/
void GLTFStaticMesh::drawMesh(const std::map<int, GLuint>& ebos, tinygltf::Mesh& mesh) {
    for (size_t i = 0; i < mesh.primitives.size(); ++i) {
        tinygltf::Primitive primitive = mesh.primitives[i];
        tinygltf::Accessor indexAccessor = model.accessors[primitive.indices];

        glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, ebos.at(indexAccessor.bufferView));

        glDrawElements(primitive.mode, indexAccessor.count,
            indexAccessor.componentType,
            ((char*)NULL + indexAccessor.byteOffset));
    }
}

/*
* Inspect a given node, draw any meshes it has, and
* recursively inspect its children
*/
void GLTFStaticMesh::drawModelNodes(tinygltf::Node& node) {
    if ((node.mesh >= 0) && (node.mesh < model.meshes.size())) {
        drawMesh(VAO_and_EBOs.second, model.meshes[node.mesh]);
    }
    for (size_t i = 0; i < node.children.size(); i++) {
        drawModelNodes(model.nodes[node.children[i]]);
    }
}

/*
* High-level method for drawing the model
*/
void GLTFStaticMesh::draw() {

    const tinygltf::Scene& scene = model.scenes[model.defaultScene];
    for (size_t i = 0; i < scene.nodes.size(); ++i) {
        drawModelNodes(model.nodes[scene.nodes[i]]);
    }
}

/*
* Bind the VAO for drawing, returns the appropriate Pre-Transform
* for the engine to use.
*/
float GLTFStaticMesh::prepareForDrawing() {
    glBindVertexArray(VAO_and_EBOs.first);
    return scale;
}

GLTFStaticMesh::~GLTFStaticMesh() {
    glDeleteVertexArrays(1, &VAO_and_EBOs.first);
    for (auto it = VAO_and_EBOs.second.cbegin(); it != VAO_and_EBOs.second.cend();) {
        glDeleteBuffers(1, &VAO_and_EBOs.second[it->first]);
        VAO_and_EBOs.second.erase(it++);
    }
}