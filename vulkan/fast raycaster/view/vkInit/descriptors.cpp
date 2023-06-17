#include "descriptors.h"
#include "../../control/logging.h"


vk::DescriptorSetLayout vkInit::make_descriptor_set_layout(
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

vk::DescriptorPool vkInit::make_descriptor_pool(
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
	catch (vk::SystemError err) {
		vkLogging::Logger::get_logger()->print("Failed to make descriptor pool");
		return nullptr;
	}
}

vk::DescriptorSet vkInit::allocate_descriptor_set(
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