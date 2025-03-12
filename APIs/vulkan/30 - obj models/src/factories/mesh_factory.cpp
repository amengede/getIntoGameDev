#include "mesh_factory.h"
#include "../logging/logger.h"
#include "../renderer/buffer.h"
#include <fstream>
#include "../backend/file.h"
#include <string>
#include <iostream>

/**
* @brief Read and transform a vertex
* 
* @param words strings of the form { "v", "x", "y", "z" }
* @param preTransform transformation to apply
* 
* @returns the loaded and transformed point
*/
vec3 read_vertex(const DynamicArray<std::string>& words,
	const mat4& preTransform) {

	vec4 pos = {
		std::stof(words[1]),
		std::stof(words[2]),
		std::stof(words[3]),
		1.0f };
	
	pos = preTransform * pos;

	return {
		pos.elements[0],
		pos.elements[1],
		pos.elements[2],
		0.0f };
}

/**
* @brief record a point
*
* @param description description of the form "v/vt/vn"
* @param v set of loaded vertices
* @param vertexLump set of flat data to populate
*/
void read_corner(std::string description,
    const DynamicArray<vec3>& v,
    DynamicArray<float>& vertexLump) {

    DynamicArray<std::string> v_vt_vn = split(description, "/");

    //position
    vec3 pos = v[std::stol(v_vt_vn[0]) - 1];
    vertexLump.push_back(pos.elements[0]);
    vertexLump.push_back(pos.elements[1]);
    vertexLump.push_back(pos.elements[2]);
	vertexLump.push_back(0.0f);

    //color
	vertexLump.push_back(1.0f);
	vertexLump.push_back(1.0f);
	vertexLump.push_back(1.0f);
	vertexLump.push_back(0.0f);
}

/**
* @brief read and triangulate a face
* 
* @param words words of the form { "f", "v/vt/vn", "v/vt/vn", ... }
* @param v set of loaded vertices
* @param vertexLump set of flat data to populate
*/
void read_face(const DynamicArray<std::string>& words,
    const DynamicArray<vec3>& v,
    DynamicArray<float>& vertexLump) {

    size_t triangleCount = words.size - 3;

    for (size_t i = 0; i < triangleCount; ++i) {
        read_corner(words[1], v, vertexLump);
        read_corner(words[2 + i], v, vertexLump);
        read_corner(words[3 + i], v, vertexLump);
    }

}

/**
* @brief Read the contents of an OBJ file and triangulate it.
* 
* @param filename name of the file to load
* @param vertexLump to be populated with triangulated data
* @param triangleCount to be populated with the triangle count
* @param preTransform Pre-Transform to apply to points
*/
void read_obj_file(const char* filename,
	DynamicArray<float>& vertexLump,
	uint32_t& triangleCount,
	const mat4& preTransform) {

    DynamicArray<vec3> v;

    size_t vertexCount = 0;
    triangleCount = 0;

    std::string line;
    DynamicArray<std::string> words;

    std::ifstream file;

    file.open(filename);
    while (std::getline(file, line)) {

        words = split(line, " ");

        if (!words[0].compare("v")) {
            ++vertexCount;
        }

        else if (!words[0].compare("f")) {
            triangleCount += words.size - 3;
        }
    }
    file.close();

    v.reserve(vertexCount);
    //three corners per triangle, 8 floats per corner
    constexpr uint32_t elementCount = 8;
    vertexLump.reserve(triangleCount * 3 * elementCount);

    file.open(filename);
    while (std::getline(file, line)) {

        words = split(line, " ");

        if (!words[0].compare("v")) {
            vec3 pos = read_vertex(words, preTransform);
            v.push_back(pos);
        }

        else if (!words[0].compare("f")) {
            read_face(words, v, vertexLump);
        }
    }
    file.close();                                                   
}

Buffer build_triangle(mem::Allocator& allocator,
	vk::CommandBuffer commandBuffer, vk::Queue queue) {

	constexpr int vertexCount = 12;

	// Make staging buffer
	size_t byteSize = vertexCount * sizeof(Vertex);
	vk::BufferUsageFlags usage = vk::BufferUsageFlagBits::eTransferSrc;
	bool hostWrite = true;
	Buffer stagingBuffer = make_buffer(allocator, byteSize, usage,
		hostWrite, "Staging Buffer");

	// Copy to staging buffer
	Vertex vertices[vertexCount] = {
		{{-0.1f,  0.1f, 2.0f}, {1.0f, 0.0f, 0.0f}},
		{{ 0.1f,  0.1f, 2.0f}, {1.0f, 0.0f, 0.0f}},
		{{ 0.0f, -0.1f, 2.0f}, {1.0f, 0.0f, 0.0f}},

		{{-0.1f,  0.3f, 4.0f}, {0.0f, 0.0f, 1.0f}},
		{{ 0.1f,  0.3f, 4.0f}, {0.0f, 0.0f, 1.0f}},
		{{ 0.0f,  0.1f, 4.0f}, {0.0f, 0.0f, 1.0f}},

		{{-0.1f,  0.2f, 3.0f}, {0.0f, 1.0f, 0.0f}},
		{{ 0.1f,  0.2f, 3.0f}, {0.0f, 1.0f, 0.0f}},
		{{ 0.0f,  0.0f, 3.0f}, {0.0f, 1.0f, 0.0f}},

		{{-0.75f,  0.4f, 1.5f}, {0.0f, 1.0f, 1.0f}},
		{{ 0.15f,  0.4f, 1.5f}, {0.0f, 1.0f, 1.0f}},
		{{ -0.3f, -0.2f, 1.5f}, {0.0f, 1.0f, 1.0f}},
	};
	void* dst;
	vmaMapMemory(allocator.allocator, stagingBuffer.allocation, &dst);
	memcpy(dst, vertices, vertexCount * sizeof(Vertex));
	vmaUnmapMemory(allocator.allocator, stagingBuffer.allocation);

	// Make Device-Local vertex buffer
	usage = vk::BufferUsageFlagBits::eStorageBuffer
		| vk::BufferUsageFlagBits::eTransferDst;
	hostWrite = false;
	Buffer vertexBuffer = make_buffer(allocator, byteSize, usage,
		hostWrite, "Vertex Buffer");

	// Copy from staging buffer
	copy(allocator.allocator, stagingBuffer, vertexBuffer, queue, commandBuffer);

	// Cleanup
	vmaDestroyBuffer(allocator.allocator, stagingBuffer.buffer, stagingBuffer.allocation);

	allocator.deletionQueue.push_back([vertexBuffer](VmaAllocator allocator) {
		vmaDestroyBuffer(allocator, vertexBuffer.buffer, vertexBuffer.allocation);
		});

	VmaAllocationInfo allocationInfo;
	vmaGetAllocationInfo(allocator.allocator, vertexBuffer.allocation, &allocationInfo);
	vertexBuffer.descriptor.buffer = vertexBuffer.buffer;
	vertexBuffer.descriptor.offset = 0;
	vertexBuffer.descriptor.range = allocationInfo.size;

	return vertexBuffer;
}

Buffer build_obj_model(mem::Allocator& allocator,
	vk::CommandBuffer commandBuffer, vk::Queue queue,
	const char* filename, const mat4& preTransform) {

	uint32_t triCount;
	DynamicArray<float> vertexLump;
	read_obj_file(filename, vertexLump, triCount, preTransform);
	Logger* logger = Logger::get_logger();
	std::cout << "Loaded model, triangle count: " << triCount << std::endl;

	// Make staging buffer
	size_t byteSize = vertexLump.size * sizeof(float);
	vk::BufferUsageFlags usage = vk::BufferUsageFlagBits::eTransferSrc;
	bool hostWrite = true;
	Buffer stagingBuffer = make_buffer(allocator, byteSize, usage, 
		hostWrite, "Staging Buffer");

	void* dst;
	vmaMapMemory(allocator.allocator, stagingBuffer.allocation, &dst);
	memcpy(dst, vertexLump.data, byteSize);
	vmaUnmapMemory(allocator.allocator, stagingBuffer.allocation);

	// Make Device-Local vertex buffer
	usage = vk::BufferUsageFlagBits::eStorageBuffer
		| vk::BufferUsageFlagBits::eTransferDst;
	hostWrite = false;
	Buffer vertexBuffer = make_buffer(allocator, byteSize, usage, 
		hostWrite, "Vertex Buffer");

	// Copy from staging buffer
	copy(allocator.allocator, stagingBuffer, vertexBuffer, queue, commandBuffer);

	// Cleanup
	vmaDestroyBuffer(allocator.allocator, stagingBuffer.buffer, stagingBuffer.allocation);

	allocator.deletionQueue.push_back([vertexBuffer](VmaAllocator allocator) {
		vmaDestroyBuffer(allocator, vertexBuffer.buffer, vertexBuffer.allocation);
	});

	VmaAllocationInfo allocationInfo;
	vmaGetAllocationInfo(allocator.allocator, vertexBuffer.allocation, &allocationInfo);
	vertexBuffer.descriptor.buffer = vertexBuffer.buffer;
	vertexBuffer.descriptor.offset = 0;
	vertexBuffer.descriptor.range = allocationInfo.size;

	vertexBuffer.triangleCount = triCount;

	return vertexBuffer;
}