#include "frame.h"
#include "image.h"

Frame::Frame(vk::Image image, vk::Device logicalDevice,
    vk::Format swapchainFormat,
    std::deque<std::function<void(vk::Device)>>& deletionQueue): image(image) {
    
    imageView = create_image_view(
        logicalDevice, image, swapchainFormat);
    VkImageView imageViewHandle = imageView;
    deletionQueue.push_back([imageViewHandle](vk::Device device) {
        vkDestroyImageView(device, imageViewHandle, nullptr);
    });
}

void Frame::set_command_buffer(vk::CommandBuffer newCommandBuffer, 
	std::vector<vk::ShaderEXT>& shaders, vk::Extent2D frameSize, 
	vk::DispatchLoaderDynamic& dl) {

	commandBuffer = newCommandBuffer;

	build_color_attachment();
	build_rendering_info(frameSize);

	vk::CommandBufferBeginInfo beginInfo = {};
	commandBuffer.begin(beginInfo);
	transition_image_layout(commandBuffer, image,
		vk::ImageLayout::eUndefined, vk::ImageLayout::eAttachmentOptimal,
		vk::AccessFlagBits::eNone, vk::AccessFlagBits::eColorAttachmentWrite,
		vk::PipelineStageFlagBits::eTopOfPipe, vk::PipelineStageFlagBits::eFragmentShader);

	annoying_boilerplate_that_dynamic_rendering_was_meant_to_spare_us(
		frameSize, dl);

	commandBuffer.beginRenderingKHR(renderingInfo, dl);

	vk::ShaderStageFlagBits stages[2] = {
		vk::ShaderStageFlagBits::eVertex,
		vk::ShaderStageFlagBits::eFragment
	};
	commandBuffer.bindShadersEXT(stages, shaders, dl);

	commandBuffer.draw(3, 1, 0, 0);

	commandBuffer.endRenderingKHR(dl);

	transition_image_layout(commandBuffer, image,
		vk::ImageLayout::eAttachmentOptimal, vk::ImageLayout::ePresentSrcKHR,
		vk::AccessFlagBits::eColorAttachmentWrite, vk::AccessFlagBits::eNone,
		vk::PipelineStageFlagBits::eFragmentShader, vk::PipelineStageFlagBits::eBottomOfPipe);

	commandBuffer.end();
}

void Frame::build_rendering_info(vk::Extent2D frameSize) {

	/*
	* // Provided by VK_VERSION_1_3
		typedef struct VkRenderingInfo {
			VkStructureType                     sType;
			const void*                         pNext;
			VkRenderingFlags                    flags;
			VkRect2D                            renderArea;
			uint32_t                            layerCount;
			uint32_t                            viewMask;
			uint32_t                            colorAttachmentCount;
			const VkRenderingAttachmentInfo*    pColorAttachments;
			const VkRenderingAttachmentInfo*    pDepthAttachment;
			const VkRenderingAttachmentInfo*    pStencilAttachment;
		} VkRenderingInfo;
	*/

	renderingInfo.setFlags(vk::RenderingFlagsKHR());
	renderingInfo.setRenderArea(vk::Rect2D({ 0,0 }, frameSize));
	renderingInfo.setLayerCount(1);
	//bitmask indicating the layers which will be rendered to
	renderingInfo.setViewMask(0);
	renderingInfo.setColorAttachmentCount(1);
	renderingInfo.setColorAttachments(colorAttachment);
}

void Frame::build_color_attachment() {
	/*
	// Provided by VK_VERSION_1_3
	typedef struct VkRenderingAttachmentInfo {
		VkStructureType          sType;
		const void*              pNext;
		VkImageView              imageView;
		VkImageLayout            imageLayout;
		VkResolveModeFlagBits    resolveMode;
		VkImageView              resolveImageView;
		VkImageLayout            resolveImageLayout;
		VkAttachmentLoadOp       loadOp;
		VkAttachmentStoreOp      storeOp;
		VkClearValue             clearValue;
	} VkRenderingAttachmentInfo;
	*/

	colorAttachment.setImageView(imageView);
	colorAttachment.setImageLayout(vk::ImageLayout::eAttachmentOptimal);
	colorAttachment.setLoadOp(vk::AttachmentLoadOp::eClear);
	colorAttachment.setStoreOp(vk::AttachmentStoreOp::eStore);
	colorAttachment.setClearValue(vk::ClearValue({ 0.5f, 0.0f, 0.25f, 1.0f }));
}

void Frame::annoying_boilerplate_that_dynamic_rendering_was_meant_to_spare_us(
	vk::Extent2D frameSize, vk::DispatchLoaderDynamic& dl) {

	vk::Viewport viewport = 
		vk::Viewport(0.0f, 0.0f, frameSize.width, frameSize.height, 0.0f, 1.0f);
	commandBuffer.setViewportWithCount(viewport, dl);

	vk::Rect2D scissor = vk::Rect2D({ 0,0 }, frameSize);
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