#include "descriptors.h"
#include "../logging/logger.h"

DescriptorSetLayoutBuilder::DescriptorSetLayoutBuilder(vk::Device& logicalDevice) : logicalDevice(logicalDevice) {}

void DescriptorSetLayoutBuilder::add_entry(vk::ShaderStageFlags stage, vk::DescriptorType type) {

	vk::DescriptorSetLayoutBinding entry = {};
	entry.setBinding(layoutBindings.size());
	entry.setDescriptorCount(1);
	entry.setDescriptorType(type);
	entry.setStageFlags(stage);

	layoutBindings.push_back(entry);
}

vk::DescriptorSetLayout DescriptorSetLayoutBuilder::build(
	std::deque<std::function<void(vk::Device)>>& deletionQueue) {

	vk::DescriptorSetLayoutCreateInfo layoutInfo;
	layoutInfo.flags = vk::DescriptorSetLayoutCreateFlagBits();
	layoutInfo.bindingCount = layoutBindings.size();
	layoutInfo.pBindings = layoutBindings.data();

	Logger* logger = Logger::get_logger();
	auto result = logicalDevice.createDescriptorSetLayout(layoutInfo);
	if (result.result != vk::Result::eSuccess) {

		logger->print("Failed to create Descriptor Set Layout");

		return nullptr;
	}
	logger->print("Created Descriptor Set Layout");
	reset();

	VkDescriptorSetLayout handle = result.value;

	deletionQueue.push_back([handle, logger](vk::Device device) {
		device.destroyDescriptorSetLayout(handle);
		logger->print("Destroyed Descriptor Set Layout");
		});
	return result.value;
}

void DescriptorSetLayoutBuilder::reset() {

	layoutBindings.clear();
}