#include "frame.h"
#include "image.h"
#include "sychronisation.h"

Frame::Frame(vk::DispatchLoaderDynamic& dl, 
	vk::Device& logicalDevice, 
	std::deque<std::function<void(vk::Device)>>& deviceDeletionQueue,
	vk::CommandBuffer commandBuffer,
	Swapchain& swapchain,
	std::vector<vk::ShaderEXT>& shaders,
	vk::Queue& queue):
	logicalDevice(logicalDevice), dl(dl), swapchain(swapchain),
	shaders(shaders), queue(queue) {
	imageAquiredSemaphore = make_semaphore(logicalDevice, deviceDeletionQueue);
	renderFinishedSemaphore = make_semaphore(logicalDevice, deviceDeletionQueue);
	renderFinishedFence = make_fence(logicalDevice, deviceDeletionQueue);
	this->commandBuffer = commandBuffer;

	renderingInfo.setFlags(vk::RenderingFlagsKHR());
	renderingInfo.setRenderArea(vk::Rect2D({ 0,0 }, swapchain.extent));
	renderingInfo.setLayerCount(1);
	//bitmask indicating the layers which will be rendered to
	renderingInfo.setViewMask(0);
	renderingInfo.setColorAttachmentCount(1);

	colorAttachment.setImageLayout(vk::ImageLayout::eAttachmentOptimal);
	colorAttachment.setLoadOp(vk::AttachmentLoadOp::eClear);
	colorAttachment.setStoreOp(vk::AttachmentStoreOp::eStore);
	colorAttachment.setClearValue(vk::ClearValue({ 0.5f, 0.0f, 0.25f, 1.0f }));
}

void Frame::acquire_image() {
	logicalDevice.waitForFences(renderFinishedFence, false, 1e9);
	logicalDevice.resetFences(renderFinishedFence);
	swapchain.lock.lock();
	imageIndex = logicalDevice.acquireNextImageKHR(
		swapchain.chain, 1e9,
		imageAquiredSemaphore, nullptr).value;
	swapchain.lock.unlock();
}

void Frame::record_draw_commands() {

	commandBuffer.reset();

	colorAttachment.setImageView(swapchain.imageViews[imageIndex]);
	renderingInfo.setColorAttachments(colorAttachment);

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

	commandBuffer.draw(3, 1, 0, 0);

	commandBuffer.endRenderingKHR(dl);

	transition_image_layout(commandBuffer, swapchain.images[imageIndex],
		vk::ImageLayout::eAttachmentOptimal, vk::ImageLayout::ePresentSrcKHR,
		vk::AccessFlagBits::eColorAttachmentWrite, vk::AccessFlagBits::eNone,
		vk::PipelineStageFlagBits::eColorAttachmentOutput, vk::PipelineStageFlagBits::eBottomOfPipe);

	commandBuffer.end();
}

void Frame::annoying_boilerplate_that_dynamic_rendering_was_meant_to_spare_us() {

	vk::Viewport viewport = 
		vk::Viewport(0.0f, 0.0f, swapchain.extent.width, swapchain.extent.height, 0.0f, 1.0f);
	commandBuffer.setViewportWithCount(viewport, dl);

	vk::Rect2D scissor = vk::Rect2D({ 0,0 }, swapchain.extent);
	commandBuffer.setScissorWithCount(scissor, dl);

	commandBuffer.setRasterizerDiscardEnable(0, dl);
	commandBuffer.setPolygonModeEXT(vk::PolygonMode::eFill, dl);
	commandBuffer.setRasterizationSamplesEXT(vk::SampleCountFlagBits::e1, dl);
	uint32_t sampleMask = 1;
	commandBuffer.setSampleMaskEXT(vk::SampleCountFlagBits::e1, sampleMask, dl);
	commandBuffer.setAlphaToCoverageEnableEXT(0, dl);
	commandBuffer.setCullMode(vk::CullModeFlagBits::eNone, dl);
	commandBuffer.setDepthTestEnable(0, dl);
	commandBuffer.setDepthWriteEnable(0, dl);
	commandBuffer.setDepthBiasEnable(0, dl);
	commandBuffer.setStencilTestEnable(0, dl);
	commandBuffer.setPrimitiveTopology(vk::PrimitiveTopology::eTriangleList, dl);
	commandBuffer.setPrimitiveRestartEnable(0, dl);
	uint32_t colorBlendEnable = 0;
	commandBuffer.setColorBlendEnableEXT(0, colorBlendEnable, dl);
	vk::ColorBlendEquationEXT equation;
	equation.colorBlendOp = vk::BlendOp::eAdd;
	equation.dstColorBlendFactor = vk::BlendFactor::eZero;
	equation.srcColorBlendFactor = vk::BlendFactor::eOne;
	commandBuffer.setColorBlendEquationEXT(0, equation, dl);
	vk::ColorComponentFlags colorWriteMask = vk::ColorComponentFlagBits::eR
		| vk::ColorComponentFlagBits::eG
		| vk::ColorComponentFlagBits::eB
		| vk::ColorComponentFlagBits::eA;
	commandBuffer.setColorWriteMaskEXT(0, colorWriteMask, dl);
}

void Frame::render() {
	vk::SubmitInfo submitInfo = {};
	submitInfo.commandBufferCount = 1;
	submitInfo.pCommandBuffers = &commandBuffer;
	submitInfo.waitSemaphoreCount = 1;
	submitInfo.pWaitSemaphores = &imageAquiredSemaphore;
	submitInfo.signalSemaphoreCount = 1;
	submitInfo.pSignalSemaphores = &renderFinishedSemaphore;
	vk::PipelineStageFlags waitStage = vk::PipelineStageFlagBits::eColorAttachmentOutput;
	submitInfo.pWaitDstStageMask = &waitStage;
	queue.submit(submitInfo, renderFinishedFence);
}

void Frame::present() {
	vk::PresentInfoKHR presentInfo = {};
	presentInfo.swapchainCount = 1;
	presentInfo.pSwapchains = &swapchain.chain;
	presentInfo.pImageIndices = &imageIndex;
	presentInfo.waitSemaphoreCount = 1;
	presentInfo.pWaitSemaphores = &renderFinishedSemaphore;
	swapchain.lock.lock();
	queue.presentKHR(presentInfo);
	swapchain.lock.unlock();
}