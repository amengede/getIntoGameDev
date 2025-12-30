#include "single_time_commands.h"

void vkUtil::startJob(vk::CommandBuffer commandBuffer) {

	commandBuffer.reset();

	vk::CommandBufferBeginInfo beginInfo;
	beginInfo.flags = vk::CommandBufferUsageFlagBits::eOneTimeSubmit;
	commandBuffer.begin(beginInfo);
}

void vkUtil::endJob(vk::CommandBuffer commandBuffer, vk::Queue submissionQueue) {

	commandBuffer.end();

	vk::SubmitInfo submitInfo;
	submitInfo.commandBufferCount = 1;
	submitInfo.pCommandBuffers = &commandBuffer;
	submissionQueue.submit(1, &submitInfo, nullptr);
	submissionQueue.waitIdle();
}