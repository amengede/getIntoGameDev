#include "mesh_factory.h"
#include "../logging/logger.h"
#include "../renderer/buffer.h"

StorageBuffer build_triangle(VmaAllocator& allocator, std::deque<std::function<void(VmaAllocator)>>& vmaDeletionQueue,
	vk::CommandBuffer commandBuffer, vk::Queue queue) {

	Logger* logger = Logger::get_logger();

	// Staging buffer
	VkBuffer stagingBuffer;
	VmaAllocation stagingAllocation;

	constexpr int vertexCount = 12;

	vk::BufferCreateInfo bufferInfo = {};
	bufferInfo.flags = vk::BufferCreateFlags();
	bufferInfo.size = vertexCount * sizeof(Vertex);
	bufferInfo.usage = vk::BufferUsageFlagBits::eTransferSrc;
	VkBufferCreateInfo bufferInfoHandle = bufferInfo;

	VmaAllocationCreateInfo allocationInfo = {};
	allocationInfo.flags = VMA_ALLOCATION_CREATE_HOST_ACCESS_SEQUENTIAL_WRITE_BIT // memory can be mapped 
		| VMA_ALLOCATION_CREATE_STRATEGY_MIN_MEMORY_BIT; // use smallest fit allocation, less fragmentation
	allocationInfo.usage = VMA_MEMORY_USAGE_AUTO;

	VmaAllocationInfo stagingAllocationInfo;

	vmaCreateBuffer(allocator, &bufferInfoHandle,
		&allocationInfo, &stagingBuffer, &stagingAllocation,
		&stagingAllocationInfo);
	vmaSetAllocationName(allocator, stagingAllocation, "Staging Buffer");
	vmaGetAllocationInfo(allocator, stagingAllocation, &stagingAllocationInfo);

	logger->log(stagingAllocationInfo);

	Vertex vertices[vertexCount] = {
		{{-0.1f,  0.1f, 0.1f}, {1.0f, 0.0f, 0.0f}},
		{{ 0.1f,  0.1f, 0.1f}, {1.0f, 0.0f, 0.0f}},
		{{ 0.0f, -0.1f, 0.1f}, {1.0f, 0.0f, 0.0f}},

		{{-0.1f,  0.3f, 0.3f}, {0.0f, 0.0f, 1.0f}},
		{{ 0.1f,  0.3f, 0.3f}, {0.0f, 0.0f, 1.0f}},
		{{ 0.0f,  0.1f, 0.3f}, {0.0f, 0.0f, 1.0f}},

		{{-0.1f,  0.2f, 0.2f}, {0.0f, 1.0f, 0.0f}},
		{{ 0.1f,  0.2f, 0.2f}, {0.0f, 1.0f, 0.0f}},
		{{ 0.0f,  0.0f, 0.2f}, {0.0f, 1.0f, 0.0f}},

		{{-0.75f,  0.4f, 0.0f}, {0.0f, 1.0f, 1.0f}},
		{{ 0.15f,  0.4f, 0.0f}, {0.0f, 1.0f, 1.0f}},
		{{ -0.3f, -0.2f, 0.0f}, {0.0f, 1.0f, 1.0f}},
	};

	void* dst;
	vmaMapMemory(allocator, stagingAllocation, &dst);
	memcpy(dst, vertices, vertexCount * sizeof(Vertex));
	vmaUnmapMemory(allocator, stagingAllocation);

	// Vertex buffer
	StorageBuffer mesh;
	VkBuffer bufferHandle;
	
	bufferInfo.usage = vk::BufferUsageFlagBits::eStorageBuffer | vk::BufferUsageFlagBits::eTransferDst;
	bufferInfoHandle = bufferInfo;

	allocationInfo.flags = VMA_ALLOCATION_CREATE_STRATEGY_MIN_MEMORY_BIT; // use smallest fit allocation, less fragmentation

	VmaAllocationInfo vertexAllocationInfo;

	vmaCreateBuffer(allocator, &bufferInfoHandle,
		&allocationInfo, &bufferHandle, &(mesh.allocation),
		&vertexAllocationInfo);
	vmaSetAllocationName(allocator, mesh.allocation, "Storage Buffer");
	vmaGetAllocationInfo(allocator, mesh.allocation, &vertexAllocationInfo);

	logger->log(vertexAllocationInfo);

	mesh.buffer = bufferHandle;

	copy(stagingBuffer, stagingAllocationInfo, bufferHandle, vertexAllocationInfo, queue, commandBuffer);

	vmaDestroyBuffer(allocator, stagingBuffer, stagingAllocation);

	vmaDeletionQueue.push_back([mesh](VmaAllocator allocator) {
		vmaDestroyBuffer(allocator, mesh.buffer, mesh.allocation);
	});

	mesh.descriptor.buffer = mesh.buffer;
	mesh.descriptor.offset = 0; // vertexAllocationInfo.offset;
	mesh.descriptor.range = vertexAllocationInfo.size;

	return mesh;
}