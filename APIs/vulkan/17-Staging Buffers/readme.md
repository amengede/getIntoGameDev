# Staging Buffers
Previously we uploaded our vertex data from the CPU and got it drawing. The GPU has multiple memory types, and it turns out the memory types with highest throughput are actually not CPU-mappable. In this tutorial we'll create two buffers: one of which will be local to our GPU, it'll hold our vertex data. The other will be a temporary CPU-mappable buffer, called a staging buffer.

We'll use VMA's allocation info to inspect our allocations.

## Buffer Creation
Creating the two buffers is actually quite simple. VMA's documentation states that it will try to choose the best memory type by default, so if we don't request write access in the allocation flags it will probably do the right thing.
```
// Staging buffer
VkBuffer stagingBuffer;
VmaAllocation stagingAllocation;

vk::BufferCreateInfo bufferInfo = {};
bufferInfo.flags = vk::BufferCreateFlags();
bufferInfo.size = 3 * sizeof(Vertex);
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

// Vertex buffer
Mesh mesh;
VkBuffer bufferHandle;

bufferInfo.usage = vk::BufferUsageFlagBits::eVertexBuffer | vk::BufferUsageFlagBits::eTransferDst;
bufferInfoHandle = bufferInfo;

allocationInfo.flags = VMA_ALLOCATION_CREATE_STRATEGY_MIN_MEMORY_BIT; // use smallest fit allocation, less fragmentation

VmaAllocationInfo vertexAllocationInfo;

vmaCreateBuffer(allocator, &bufferInfoHandle,
	&allocationInfo, &bufferHandle, &(mesh.allocation),
	&vertexAllocationInfo);
```

## Inspecting Allocations
Anytime the words "probably" or "tries to" come up, even in official documentation, it's not a bad idea to try verify for ourselves. Did VMA allocate these two buffers to different memory types? Let's build a function to print a vma allocation.

```
void Logger::log(const VmaAllocationInfo& allocationInfo) {

	if (!enabled) {
		return;
	}

	std::cout << "---- " << allocationInfo.pName << " ----" << std::endl;
	std::cout << "\tMemory type: " << allocationInfo.memoryType << std::endl;
	std::cout << "\tMemory object: " << allocationInfo.deviceMemory << std::endl;
	std::cout << "\tOffset: " << allocationInfo.offset << std::endl;
	std::cout << "\tSize: " << allocationInfo.size << std::endl;
}
```

Buffer creation will fill all of these fields except the name, which we can fill ourselves.
```
vmaCreateBuffer(allocator, &bufferInfoHandle,
	&allocationInfo, &stagingBuffer, &stagingAllocation,
	&stagingAllocationInfo);
vmaSetAllocationName(allocator, stagingAllocation, "Staging Buffer");
vmaGetAllocationInfo(allocator, stagingAllocation, &stagingAllocationInfo);

logger->log(stagingAllocationInfo);
```

Logging out both allocations verifies that they are indeed not aliasing the same buffer.

## Transfering between buffers
Currently we should have our vertex data copied in and ready to go on our staging buffer, we just need to get it to the vertex buffer. Although the vertex buffer can't be mapped from the CPU, we can submit a transfer job on the GPU. For this, I'll write a helper function.

```
void copy(
	vk::Buffer srcBuffer, VmaAllocationInfo& srcInfo,
	vk::Buffer dstBuffer, VmaAllocationInfo& dstInfo,
	vk::Queue queue, vk::CommandBuffer commandBuffer) {

	// Copy from staging buffer to vertex buffer
	commandBuffer.reset();
	vk::CommandBufferBeginInfo beginInfo;
	beginInfo.flags = vk::CommandBufferUsageFlagBits::eOneTimeSubmit;
	commandBuffer.begin(beginInfo);

	vk::BufferCopy copyRegion;
	copyRegion.srcOffset = srcInfo.offset;
	copyRegion.dstOffset = dstInfo.offset;
	copyRegion.size = srcInfo.size;
	commandBuffer.copyBuffer(srcBuffer, dstBuffer, 1, &copyRegion);

	commandBuffer.end();

	vk::SubmitInfo submitInfo;
	submitInfo.commandBufferCount = 1;
	submitInfo.pCommandBuffers = &commandBuffer;
	queue.submit(1, &submitInfo, nullptr);
	queue.waitIdle();

}
```

It will take some refactoring, but otherwise it's quite straightforward to copy between the two buffers. After copying we can destroy the staging buffer, and record a destructor for the vertex buffer.
```
copy(stagingBuffer, stagingAllocationInfo, bufferHandle, vertexAllocationInfo, queue, commandBuffer);

vmaDestroyBuffer(allocator, stagingBuffer, stagingAllocation);

vmaDeletionQueue.push_back([mesh](VmaAllocator allocator) {
	vmaDestroyBuffer(allocator, mesh.buffer, mesh.allocation);
});
```