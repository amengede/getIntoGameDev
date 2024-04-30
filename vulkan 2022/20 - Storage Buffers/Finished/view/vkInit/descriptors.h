#pragma once
#include "../../config.h"

namespace vkInit {

	/**
		Describes the bindings of a descriptor set layout
	*/
	struct descriptorSetLayoutData {
		int count;
		std::vector<int> indices;
		std::vector<vk::DescriptorType> types;
		std::vector<int> counts;
		std::vector<vk::ShaderStageFlags> stages;
	};

	/**
		Make a descriptor set layout from the given descriptions

		\param device the logical device
		\param bindings	a struct describing the bindings used in the shader
		\returns the created descriptor set layout
	*/
	vk::DescriptorSetLayout make_descriptor_set_layout(
		vk::Device device, const descriptorSetLayoutData& bindings) {

		/*
			Bindings describes a whole bunch of descriptor types, collect them all into a
			list of some kind.
		*/
		std::vector<vk::DescriptorSetLayoutBinding> layoutBindings;
		layoutBindings.reserve(bindings.count);

		for (int i = 0; i < bindings.count; i++) {

			/*
				typedef struct VkDescriptorSetLayoutBinding {
					uint32_t              binding;
					VkDescriptorType      descriptorType;
					uint32_t              descriptorCount;
					VkShaderStageFlags    stageFlags;
					const VkSampler*      pImmutableSamplers;
				} VkDescriptorSetLayoutBinding;
			*/

			vk::DescriptorSetLayoutBinding layoutBinding;
			layoutBinding.binding = bindings.indices[i];
			layoutBinding.descriptorType = bindings.types[i];
			layoutBinding.descriptorCount = bindings.counts[i];
			layoutBinding.stageFlags = bindings.stages[i];
			layoutBindings.push_back(layoutBinding);
		}

		/*
			typedef struct VkDescriptorSetLayoutCreateInfo {
				VkStructureType                        sType;
				const void*                            pNext;
				VkDescriptorSetLayoutCreateFlags       flags;
				uint32_t                               bindingCount;
				const VkDescriptorSetLayoutBinding*    pBindings;
			} VkDescriptorSetLayoutCreateInfo;
		*/
		vk::DescriptorSetLayoutCreateInfo layoutInfo;
		layoutInfo.flags = vk::DescriptorSetLayoutCreateFlagBits();
		layoutInfo.bindingCount = bindings.count;
		layoutInfo.pBindings = layoutBindings.data();


		try {
			return device.createDescriptorSetLayout(layoutInfo);
		}
		catch (vk::SystemError err) {

			vkLogging::Logger::get_logger()->print("Failed to create Descriptor Set Layout");

			return nullptr;
		}
	}

	/**
		Make a descriptor pool

		\param device the logical device
		\param size the number of descriptor sets to allocate from the pool
		\param bindings	used to get the descriptor types
		\returns the created descriptor pool
	*/
	vk::DescriptorPool make_descriptor_pool(
		vk::Device device, uint32_t size, const descriptorSetLayoutData& bindings) {

		std::vector<vk::DescriptorPoolSize> poolSizes;
		/*
			typedef struct VkDescriptorPoolSize {
				VkDescriptorType    type;
				uint32_t            descriptorCount;
			} VkDescriptorPoolSize;
		*/

		for (int i = 0; i < bindings.count; i++) {

			vk::DescriptorPoolSize poolSize;
			poolSize.type = bindings.types[i];
			poolSize.descriptorCount = size;
			poolSizes.push_back(poolSize);
		}

		vk::DescriptorPoolCreateInfo poolInfo;
		/*
			typedef struct VkDescriptorPoolCreateInfo {
				VkStructureType                sType;
				const void*                    pNext;
				VkDescriptorPoolCreateFlags    flags;
				uint32_t                       maxSets;
				uint32_t                       poolSizeCount;
				const VkDescriptorPoolSize*    pPoolSizes;
			} VkDescriptorPoolCreateInfo;
		*/

		poolInfo.flags = vk::DescriptorPoolCreateFlags();
		poolInfo.maxSets = size;
		poolInfo.poolSizeCount = static_cast<uint32_t>(poolSizes.size());
		poolInfo.pPoolSizes = poolSizes.data();

		try {
			return device.createDescriptorPool(poolInfo);
		}
		catch (vk::SystemError err){
			vkLogging::Logger::get_logger()->print("Failed to make descriptor pool");
			return nullptr;
		}
	}

	/**
		Allocate a descriptor set from a pool.

		\param device the logical device
		\param descriptorPool the pool to allocate from
		\param layout the descriptor set layout which the set must adhere to
		\returns the allocated descriptor set
	*/
	vk::DescriptorSet allocate_descriptor_set(
		vk::Device device, vk::DescriptorPool descriptorPool, 
		vk::DescriptorSetLayout layout) {

		vk::DescriptorSetAllocateInfo allocationInfo;
		/*
			typedef struct VkDescriptorSetAllocateInfo {
				VkStructureType                 sType;
				const void*                     pNext;
				VkDescriptorPool                descriptorPool;
				uint32_t                        descriptorSetCount;
				const VkDescriptorSetLayout*    pSetLayouts;
			} VkDescriptorSetAllocateInfo;
		*/

		allocationInfo.descriptorPool = descriptorPool;
		allocationInfo.descriptorSetCount = 1;
		allocationInfo.pSetLayouts = &layout;

		try {
			return device.allocateDescriptorSets(allocationInfo)[0];
		}
		catch (vk::SystemError err) {
			vkLogging::Logger::get_logger()->print("Failed to allocate descriptor set from pool");
			return nullptr;
		}
	}
}