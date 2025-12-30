#include "mesh_factory.h"

Mesh build_triangle(VmaAllocator& allocator, std::deque<std::function<void(VmaAllocator)>>& vmaDeletionQueue) {
	Mesh mesh;

	vk::BufferCreateInfo bufferInfo = {};
	bufferInfo.flags = vk::BufferCreateFlags();
	bufferInfo.size = 3 * sizeof(Vertex);
	bufferInfo.usage = vk::BufferUsageFlagBits::eVertexBuffer | vk::BufferUsageFlagBits::eTransferDst;
	VkBufferCreateInfo bufferInfoHandle = bufferInfo;

	VmaAllocationCreateInfo allocationInfo = {};
	allocationInfo.flags = VMA_ALLOCATION_CREATE_HOST_ACCESS_SEQUENTIAL_WRITE_BIT // memory can be mapped 
		| VMA_ALLOCATION_CREATE_STRATEGY_MIN_MEMORY_BIT; // use smallest fit allocation, less fragmentation
	allocationInfo.usage = VMA_MEMORY_USAGE_AUTO;

	VkBuffer bufferHandle;
	VmaAllocationInfo vmaAllocationInfo;

	vmaCreateBuffer(allocator, &bufferInfoHandle,
		&allocationInfo, &bufferHandle, &mesh.allocation, 
		&vmaAllocationInfo);

	mesh.buffer = bufferHandle;
	mesh.offset = vmaAllocationInfo.offset;

	Vertex vertices[3] = {
		{{-0.75f,  0.75f}, {1.0f, 0.0f, 0.0f}},
		{{ 0.75f,  0.75f}, {0.0f, 1.0f, 0.0f}},
		{{  0.0f, -0.75f}, {0.0f, 0.0f, 1.0f}}
	};

	void* dst;
	vmaMapMemory(allocator, mesh.allocation, &dst);
	memcpy(dst, vertices, 3 * sizeof(Vertex));
	vmaUnmapMemory(allocator, mesh.allocation);

	vmaDeletionQueue.push_back([mesh](VmaAllocator allocator) {
		vmaDestroyBuffer(allocator, mesh.buffer, mesh.allocation);
	});

	return mesh;
}