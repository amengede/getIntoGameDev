# Vertex Buffers
Now instead of hardcoding our data, let's send data from the CPU to the GPU. This decomposes into a few subtasks:

1. Tell the GPU how to interpret the data it's going to get.
1. Allocate and fill a buffer with the data we want to use.
1. Make sure everything works (debug, probably a lot)

## Telling the GPU about the data: binding descriptions and attributes
Firstly, let's add a source file to construct meshes for us. Inside, let's add a struct to describe our vertices.
```
struct Vertex {
	glm::vec2 pos;
	glm::vec3 color;
};
```
In order to use vertex data, two aspects must be described: the binding and the attributes. A binding description describes the logistic side of the data, how big it is and how it will be consumed by the shaders. The attributes, on the other hand, describe the semantics of the data, how to unpack individual attributes from each vertex.

Let's start with the binding description, note that here I'm using the 2EXT variant, since that's what the dynamic rendering boilderplate expects.
```
static vk::VertexInputBindingDescription2EXT getBindingDescription() {

	vk::VertexInputBindingDescription2EXT description = {};
	description.binding = 0;
	description.stride = sizeof(Vertex);
	description.inputRate = vk::VertexInputRate::eVertex;
    description.divisor = 1;
	return description;
}
```

And now the attributes can be described:
```
static std::vector<vk::VertexInputAttributeDescription2EXT> getAttributeDescriptions() {
	std::vector<vk::VertexInputAttributeDescription2EXT> attributes(2);

	attributes[0].binding = 0;
	attributes[0].location = 0;
	attributes[0].format = vk::Format::eR32G32Sfloat;
	attributes[0].offset = offsetof(Vertex, pos);

	attributes[1].binding = 0;
	attributes[1].location = 1;
	attributes[1].format = vk::Format::eR32G32B32Sfloat;
	attributes[1].offset = offsetof(Vertex, color);

	return attributes;
}
```

This info can then be fetched and used by the frame.
```
void Frame::annoying_boilerplate_that_dynamic_rendering_was_meant_to_spare_us() {

	vk::VertexInputBindingDescription2EXT bindingDescription = Vertex::getBindingDescription();
	std::vector<vk::VertexInputAttributeDescription2EXT> attributes = Vertex::getAttributeDescriptions();
	commandBuffer.setVertexInputEXT(1, &bindingDescription, 2, attributes.data(), dl);
    // ...
}
```

Edit the shader to remove the hardcoded data and, tada! A blank screen!

## Sending the data: buffers
Normally creating a buffer in Vulkan involves requesting a chunk of memory, however since this series is about a more modern, dynamic approach, I'll be using the Vulkan Memory Allocator to handle this. VMA is a header only library, we simply need to copy the header file into our dependencies, and create a single cpp file to serve as the implementation unit.
```
#define VMA_IMPLEMENTATION
#include <vma/vk_mem_alloc.h>
```

The Engine will now have an allocator, as well as a dedicated deletion queue.
```
#pragma once
// ...
#include <vma/vk_mem_alloc.h>
#include "../factories/mesh_factory.h"

class Engine {

private:

    std::deque<std::function<void(VmaAllocator)>> vmaDeletionQueue;

    VmaAllocator allocator;
};
```

The allocator depends on the Instance, Logical and Physical devices, so it must be created after those three have been initialized.
```
VmaAllocatorCreateInfo allocatorInfo = {};
allocatorInfo.device = logicalDevice;
allocatorInfo.instance = instance;
allocatorInfo.physicalDevice = physicalDevice;
allocatorInfo.vulkanApiVersion = vk::makeApiVersion(1, 3, 0, 0);
vmaCreateAllocator(&allocatorInfo, &allocator);
```

The destructor will flush the allocator queue, then destroy the allocator itself. Since the allocator depends on the logical device, it should be destroyed first.

```
Engine::~Engine() {

	graphicsQueue.waitIdle();

	logger->print("Goodbye see you!");

	while (vmaDeletionQueue.size() > 0) {
		vmaDeletionQueue.back()(allocator);
		vmaDeletionQueue.pop_back();
	}

	vmaDestroyAllocator(allocator);

	swapchain.destroy(logicalDevice);

	while (deviceDeletionQueue.size() > 0) {
		deviceDeletionQueue.back()(logicalDevice);
		deviceDeletionQueue.pop_back();
	}

	while (instanceDeletionQueue.size() > 0) {
		instanceDeletionQueue.back()(instance);
		instanceDeletionQueue.pop_back();
	}
}
```

Now let's define a struct to represent a mesh. VMA populates an allocation object to hold things such as the buffer's backing memory, so we'll need to store that along with the vulkan buffer. In future I'll be allocating several meshes to the same memory allocation, and so it'll be useful to store each buffer's offset.

```
struct Mesh {
	vk::Buffer buffer;
	VmaAllocation allocation;
	vk::DeviceSize offset;
};
```

Now for the building function. We'll take in an allocator object and a deletion queue, and return a Mesh.

```
Mesh build_triangle(VmaAllocator& allocator, std::deque<std::function<void(VmaAllocator)>>& vmaDeletionQueue) {
	Mesh mesh;

	return mesh;
}
```

Firstly we describe the vulkan buffer we'd like to build.

```
	vk::BufferCreateInfo bufferInfo = {};
	bufferInfo.flags = vk::BufferCreateFlags();
	bufferInfo.size = 3 * sizeof(Vertex);
	bufferInfo.usage = vk::BufferUsageFlagBits::eVertexBuffer | vk::BufferUsageFlagBits::eTransferDst;
	VkBufferCreateInfo bufferInfoHandle = bufferInfo;
```

Then we tell VMA how we'd like to allocate memory for the vulkan buffer.

```
	VmaAllocationCreateInfo allocationInfo = {};
	allocationInfo.flags = VMA_ALLOCATION_CREATE_HOST_ACCESS_SEQUENTIAL_WRITE_BIT // memory can be mapped 
		| VMA_ALLOCATION_CREATE_STRATEGY_MIN_MEMORY_BIT; // use smallest fit allocation, less fragmentation
	allocationInfo.usage = VMA_MEMORY_USAGE_AUTO;
```

Once the creation info is built, we instruct VMA to make the buffer, we then read back the offset from the allocationInfo struct which the allocator populated. Some of the awkwardness in this code comes from the fact that VMA is built for a C API rather than C++.

```
	VkBuffer bufferHandle;
	VmaAllocationInfo vmaAllocationInfo;

	vmaCreateBuffer(allocator, &bufferInfoHandle,
		&allocationInfo, &bufferHandle, &mesh.allocation, 
		&vmaAllocationInfo);

	mesh.buffer = bufferHandle;
	mesh.offset = vmaAllocationInfo.offset;
```

Now the buffer should be constructed, we can fill it with Vertex data and register a destructor for it.

```
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
```

We are tantalizingly close! All that remains is for the frames to consume the mesh,
```
Frame::Frame(Swapchain& swapchain, vk::Device logicalDevice,
	std::vector<vk::ShaderEXT>& shaders,
	vk::DispatchLoaderDynamic& dl,
	vk::CommandBuffer commandBuffer,
	std::deque<std::function<void(vk::Device)>>& deletionQueue,
	Mesh* trianglemesh): swapchain(swapchain), shaders(shaders), 
		dl(dl) {
   
	this->commandBuffer = commandBuffer;
	this->triangleMesh = trianglemesh;

	imageAquiredSemaphore = make_semaphore(logicalDevice, deletionQueue);
	renderFinishedSemaphore = make_semaphore(logicalDevice, deletionQueue);
	renderFinishedFence = make_fence(logicalDevice, deletionQueue);
}
```

And bind the vertex buffer!
```
void Frame::record_command_buffer(uint32_t imageIndex) {

	commandBuffer.reset();

	build_color_attachment(imageIndex);
	build_rendering_info();

	vk::CommandBufferBeginInfo beginInfo = {};
	commandBuffer.begin(beginInfo);
	transition_image_layout(commandBuffer, swapchain.images[imageIndex],
		vk::ImageLayout::eUndefined, vk::ImageLayout::eAttachmentOptimal,
		vk::AccessFlagBits::eNone, vk::AccessFlagBits::eColorAttachmentWrite,
		vk::PipelineStageFlagBits::eTopOfPipe, vk::PipelineStageFlagBits::eColorAttachmentOutput);

	annoying_boilerplate_that_dynamic_rendering_was_meant_to_spare_us();

	commandBuffer.beginRenderingKHR(renderingInfo, dl);

	vk::ShaderStageFlagBits stages[2] = {
		vk::ShaderStageFlagBits::eVertex,
		vk::ShaderStageFlagBits::eFragment
	};
	commandBuffer.bindShadersEXT(stages, shaders, dl);

	commandBuffer.bindVertexBuffers(0, 1, &(triangleMesh->buffer), &(triangleMesh->offset));

	commandBuffer.draw(3, 1, 0, 0);

	commandBuffer.endRenderingKHR(dl);

	transition_image_layout(commandBuffer, swapchain.images[imageIndex],
		vk::ImageLayout::eAttachmentOptimal, vk::ImageLayout::ePresentSrcKHR,
		vk::AccessFlagBits::eColorAttachmentWrite, vk::AccessFlagBits::eNone,
		vk::PipelineStageFlagBits::eColorAttachmentOutput, vk::PipelineStageFlagBits::eBottomOfPipe);

	commandBuffer.end();
}
```