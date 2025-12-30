#include "model_factory.h"
#include "../stb_image.h"

StaticMesh MeshFactory::build_gltf_mesh(const char* objectName) {
    StaticMesh mesh;
    std::stringstream filenameBuilder;
    std::string filename;

    //Build gltf filename
    filenameBuilder << "models/" << objectName << "/" << objectName << ".gltf";
    filename = filenameBuilder.str();
    filenameBuilder.str("");
    Json::Value jsonContents = read_gltf_file(filename.c_str());

    //Build binary filename
    filenameBuilder << "models/" << objectName << "/" << objectName << ".bin";
    filename = filenameBuilder.str();
    filenameBuilder.str("");
    std::vector<char> binaryContents = read_binary_file(filename.c_str());

    //Populate attributes
    fetch_vec3("POSITION", jsonContents, binaryContents, v);
    fetch_vec3("NORMAL", jsonContents, binaryContents, vn);
    fetch_vec2("TEXCOORD_0", jsonContents, binaryContents, vt);
    fetch_indices(jsonContents, binaryContents);

    //Put it all together
    load_material(objectName, jsonContents, mesh);
    build_vertices();
    build_buffers(mesh);
    describe_attributes();

    return mesh;
}

Json::Value MeshFactory::read_gltf_file(const char* filename) {
    std::ifstream jsonFile;
    Json::Value fileContents;

    jsonFile.open(filename, std::ios::binary);

    jsonFile >> fileContents;

    jsonFile.close();

    return fileContents;
}

std::vector<char> MeshFactory::read_binary_file(const char* filename) {

    std::ifstream binaryFile;
    std::vector<char> byteData;

    //Open the file, get its size.
    binaryFile.open(filename, std::ios::binary | std::ios::ate);
    size_t byteCount = binaryFile.tellg();
    byteData.resize(byteCount);
    binaryFile.seekg(0);

    //Now read the file
    binaryFile.read(byteData.data(), byteCount);
    binaryFile.close();

    return byteData;
}

void MeshFactory::fetch_vec3(const char* attributeName,
    Json::Value& gltfData, std::vector<char>& byteData,
    std::vector<glm::vec3>& dst) {

    int accessor_index = gltfData["meshes"][0]["primitives"][0]["attributes"][attributeName].asInt();
    int buffer_view = gltfData["accessors"][accessor_index]["bufferView"].asInt();
    int count = gltfData["accessors"][accessor_index]["count"].asInt();
    dst.resize(count);
    int byte_length = gltfData["bufferViews"][buffer_view]["byteLength"].asInt();
    int offset = gltfData["bufferViews"][buffer_view]["byteOffset"].asInt();
    memcpy(dst.data(), byteData.data() + offset, byte_length);
}

void MeshFactory::fetch_vec2(const char* attributeName,
    Json::Value& gltfData, std::vector<char>& byteData,
    std::vector<glm::vec2>& dst) {

    int accessor_index = gltfData["meshes"][0]["primitives"][0]["attributes"][attributeName].asInt();
    int buffer_view = gltfData["accessors"][accessor_index]["bufferView"].asInt();
    int count = gltfData["accessors"][accessor_index]["count"].asInt();
    dst.resize(count);
    int byte_length = gltfData["bufferViews"][buffer_view]["byteLength"].asInt();
    int offset = gltfData["bufferViews"][buffer_view]["byteOffset"].asInt();
    memcpy(dst.data(), byteData.data() + offset, byte_length);
}

void MeshFactory::fetch_indices(Json::Value& gltfData, std::vector<char>& byteData) {
    int accessor_index = gltfData["meshes"][0]["primitives"][0]["indices"].asInt();
    int buffer_view = gltfData["accessors"][accessor_index]["bufferView"].asInt();
    int count = gltfData["accessors"][accessor_index]["count"].asInt();
    indices.resize(count);
    int byte_length = gltfData["bufferViews"][buffer_view]["byteLength"].asInt();
    int offset = gltfData["bufferViews"][buffer_view]["byteOffset"].asInt();
    memcpy(indices.data(), byteData.data() + offset, byte_length);
}

void MeshFactory::load_material(const char* objectName, Json::Value& gltfData, StaticMesh& mesh) {

    std::stringstream filenameBuilder;
    filenameBuilder << "models/" << objectName << "/" << gltfData["images"][0]["uri"].asString();
    std::string filename = filenameBuilder.str();
    int width, height, channels;
    stbi_set_flip_vertically_on_load(true);
    unsigned char* data = stbi_load(
        filename.c_str(), &width, &height, &channels, STBI_rgb_alpha);

    glGenTextures(1, &mesh.material);
    glBindTexture(GL_TEXTURE_2D, mesh.material);
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_CLAMP_TO_EDGE);
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_CLAMP_TO_EDGE);
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST);
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR);
    glTexStorage2D(GL_TEXTURE_2D, 1, GL_RGBA8, width, height);
    glTexSubImage2D(GL_TEXTURE_2D, 
        0, 0, 0, 
        width, height,
        GL_RGBA, GL_UNSIGNED_BYTE, data);

    stbi_image_free(data);
}

void MeshFactory::build_vertices() {

    size_t vertexCount = v.size();
    vertices.resize(vertexCount);

    for (size_t i = 0; i < vertexCount; ++i) {
        Vertex vertex;
        vertex.position = v[i];
        vertex.texCoord = vt[i];
        vertex.normal = vn[i];
        vertices[i] = vertex;
    }
}

void MeshFactory::build_buffers(StaticMesh& mesh) {

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
}

void MeshFactory::describe_attributes() {

    //position
    glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, 32, (void*)0);
    glEnableVertexAttribArray(0);
    //texture coordinates
    glVertexAttribPointer(1, 2, GL_FLOAT, GL_FALSE, 32, (void*)12);
    glEnableVertexAttribArray(1);
    //normal
    glVertexAttribPointer(2, 3, GL_FLOAT, GL_FALSE, 32, (void*)20);
    glEnableVertexAttribArray(2);

}