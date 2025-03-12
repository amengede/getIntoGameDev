#include "command.h"

vk::CommandPool make_command_pool(Device device,
	uint32_t queueFamilyIndex) {

	Logger* logger = Logger::get_logger();

	vk::CommandPoolCreateInfo poolInfo = {};
	poolInfo.setFlags(vk::CommandPoolCreateFlags()
		| vk::CommandPoolCreateFlagBits::eResetCommandBuffer);
	poolInfo.setQueueFamilyIndex(queueFamilyIndex);

	vk::CommandPool pool = nullptr;

	auto result = device.device.createCommandPool(poolInfo);
	if (result.result == vk::Result::eSuccess) {
		logger->print("Command pool created successfully");
		pool = result.value;
		device.deletionQueue.push_back([logger, pool](vk::Device device) {
			device.destroyCommandPool(pool);
			logger->print("Destroyed command pool!");
			});
	}
	else {
		logger->print("Command pool creation failed");
	}
	return pool;
}

vk::CommandBuffer allocate_command_buffer(vk::Device logicalDevice,
	vk::CommandPool commandPool) {
	
	vk::CommandBufferAllocateInfo allocInfo = {};
	allocInfo.setCommandBufferCount(1);
	allocInfo.setCommandPool(commandPool);
	allocInfo.setLevel(vk::CommandBufferLevel::ePrimary);
	return logicalDevice.allocateCommandBuffers(allocInfo).value[0];
}