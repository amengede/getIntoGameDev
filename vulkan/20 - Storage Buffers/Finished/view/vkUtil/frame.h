#pragma once
#include "../../config.h"
#include "memory.h"

namespace vkUtil {

	/**
		Describes the data to send to the shader for each frame.
	*/
	struct UBO {
		glm::mat4 view;
		glm::mat4 projection;
		glm::mat4 viewProjection;
	};

	/**
		Holds the data structures associated with a "Frame"
	*/
	struct SwapChainFrame {

		//Swapchain-type stuff
		vk::Image image;
		vk::ImageView imageView;
		vk::Framebuffer framebuffer;

		vk::CommandBuffer commandBuffer;

		//Sync objects
		vk::Semaphore imageAvailable, renderFinished;
		vk::Fence inFlight;

		//Resources
		UBO cameraData;
		Buffer cameraDataBuffer;
		void* cameraDataWriteLocation;
		std::vector<glm::mat4> modelTransforms;
		Buffer modelBuffer;
		void* modelBufferWriteLocation;

		//Resource Descriptors
		vk::DescriptorBufferInfo uniformBufferDescriptor;
		vk::DescriptorBufferInfo modelBufferDescriptor;
		vk::DescriptorSet descriptorSet;

		void make_descriptor_resources(vk::Device logicalDevice, vk::PhysicalDevice physicalDevice) {

			BufferInputChunk input;
			input.logicalDevice = logicalDevice;
			input.memoryProperties = vk::MemoryPropertyFlagBits::eHostVisible | vk::MemoryPropertyFlagBits::eHostCoherent;
			input.physicalDevice = physicalDevice;
			input.size = sizeof(UBO);
			input.usage = vk::BufferUsageFlagBits::eUniformBuffer;
			cameraDataBuffer = createBuffer(input);

			cameraDataWriteLocation = logicalDevice.mapMemory(cameraDataBuffer.bufferMemory, 0, sizeof(UBO));

			input.size = 1024 * sizeof(glm::mat4);
			input.usage = vk::BufferUsageFlagBits::eStorageBuffer;
			modelBuffer = createBuffer(input);

			modelBufferWriteLocation = logicalDevice.mapMemory(modelBuffer.bufferMemory, 0, 1024 * sizeof(glm::mat4));

			modelTransforms.reserve(1024);
			for (int i = 0; i < 1024; ++i) {
				modelTransforms.push_back(glm::mat4(1.0f));
			}
			
			/*
			typedef struct VkDescriptorBufferInfo {
				VkBuffer        buffer;
				VkDeviceSize    offset;
				VkDeviceSize    range;
			} VkDescriptorBufferInfo;
			*/
			uniformBufferDescriptor.buffer = cameraDataBuffer.buffer;
			uniformBufferDescriptor.offset = 0;
			uniformBufferDescriptor.range = sizeof(UBO);

			modelBufferDescriptor.buffer = modelBuffer.buffer;
			modelBufferDescriptor.offset = 0;
			modelBufferDescriptor.range = 1024 * sizeof(glm::mat4);

		}

		void write_descriptor_set(vk::Device device) {

			vk::WriteDescriptorSet writeInfo;
			/*
			typedef struct VkWriteDescriptorSet {
				VkStructureType                  sType;
				const void* pNext;
				VkDescriptorSet                  dstSet;
				uint32_t                         dstBinding;
				uint32_t                         dstArrayElement;
				uint32_t                         descriptorCount;
				VkDescriptorType                 descriptorType;
				const VkDescriptorImageInfo* pImageInfo;
				const VkDescriptorBufferInfo* pBufferInfo;
				const VkBufferView* pTexelBufferView;
			} VkWriteDescriptorSet;
			*/

			writeInfo.dstSet = descriptorSet;
			writeInfo.dstBinding = 0;
			writeInfo.dstArrayElement = 0; //byte offset within binding for inline uniform blocks
			writeInfo.descriptorCount = 1;
			writeInfo.descriptorType = vk::DescriptorType::eUniformBuffer;
			writeInfo.pBufferInfo = &uniformBufferDescriptor;

			device.updateDescriptorSets(writeInfo, nullptr);

			vk::WriteDescriptorSet writeInfo2;
			writeInfo2.dstSet = descriptorSet;
			writeInfo2.dstBinding = 1;
			writeInfo2.dstArrayElement = 0; //byte offset within binding for inline uniform blocks
			writeInfo2.descriptorCount = 1;
			writeInfo2.descriptorType = vk::DescriptorType::eStorageBuffer;
			writeInfo2.pBufferInfo = &modelBufferDescriptor;

			device.updateDescriptorSets(writeInfo2, nullptr);
		}
	};

}