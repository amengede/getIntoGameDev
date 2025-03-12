#include "descriptors.h"
#include "../logging/logger.h"

DescriptorSetLayoutBuilder::DescriptorSetLayoutBuilder(Device& device):
	device(device) {}

void DescriptorSetLayoutBuilder::add_entry(vk::ShaderStageFlags stage,
	vk::DescriptorType type) {

	vk::DescriptorSetLayoutBinding entry = {};
	entry.setBinding(static_cast<uint32_t>(layoutBindings.size));
	entry.setDescriptorCount(1);
	entry.setDescriptorType(type);
	entry.setStageFlags(stage);
	entry.setPImmutableSamplers(nullptr);

	layoutBindings.push_back(entry);
}

vk::DescriptorSetLayout DescriptorSetLayoutBuilder::build() {

	vk::DescriptorSetLayoutCreateInfo layoutInfo;
	layoutInfo.flags = vk::DescriptorSetLayoutCreateFlagBits();
	layoutInfo.bindingCount = static_cast<uint32_t>(layoutBindings.size);
	layoutInfo.pBindings = layoutBindings.data;

	Logger* logger = Logger::get_logger();
	auto result = device.device.createDescriptorSetLayout(layoutInfo);
	if (result.result != vk::Result::eSuccess) {

		logger->print("Failed to create Descriptor Set Layout");

		return nullptr;
	}
	logger->print("Created Descriptor Set Layout");
	reset();

	VkDescriptorSetLayout handle = result.value;

	device.deletionQueue.push_back([handle, logger](vk::Device device) {
		device.destroyDescriptorSetLayout(handle);
		logger->print("Destroyed Descriptor Set Layout");
		});
	return result.value;
}

void DescriptorSetLayoutBuilder::reset() {

	layoutBindings.clear();
}

vk::DescriptorPool make_descriptor_pool(
	Device device, uint32_t descriptorSetCount,
	DynamicArray<vk::DescriptorType> bindingTypes) {

	DynamicArray<vk::DescriptorPoolSize> poolSizes;
	/*
		typedef struct VkDescriptorPoolSize {
			VkDescriptorType    type;
			uint32_t            descriptorCount;
		} VkDescriptorPoolSize;
	*/

	for (uint32_t i = 0; i < bindingTypes.size; i++) {

		vk::DescriptorPoolSize poolSize;
		poolSize.type = bindingTypes[i];
		poolSize.descriptorCount = 1;
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
	poolInfo.maxSets = descriptorSetCount;
	poolInfo.poolSizeCount = static_cast<uint32_t>(poolSizes.size);
	poolInfo.pPoolSizes = poolSizes.data;

	auto result = device.device.createDescriptorPool(poolInfo);
	Logger* logger = Logger::get_logger();
	if (result.result != vk::Result::eSuccess) {
		logger->print("failed to create descriptor pool");
		return nullptr;
	}
	logger->print("successfully created descriptor pool");

	VkDescriptorPool handle = result.value;
	device.deletionQueue.push_back([handle, logger](vk::Device device) {
		device.destroyDescriptorPool(handle);
		logger->print("Destroyed Descriptor Pool");
	});

	return result.value;
}

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

	Logger* logger = Logger::get_logger();

	auto result = device.allocateDescriptorSets(allocationInfo);
	if (result.result != vk::Result::eSuccess) {
		logger->print("Failed to allocate Descriptor Set");
		return nullptr;
	}
	logger->print("Successfully allocated a Descriptor Set");

	return result.value[0];
}