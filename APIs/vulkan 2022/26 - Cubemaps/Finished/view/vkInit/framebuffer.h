#pragma once
#include "../../config.h"
#include "../vkUtil/frame.h"

namespace vkInit {

	/**
		Data structures involved in making framebuffers for the
		swapchain.
	*/
	struct framebufferInput {
		vk::Device device;
		std::unordered_map<pipelineType, vk::RenderPass> renderpass;
		vk::Extent2D swapchainExtent;
	};

	/**
		Make framebuffers for the swapchain

		\param inputChunk required input for creation
		\param frames the vector to be populated with the created framebuffers
	*/
	void make_framebuffers(framebufferInput inputChunk, std::vector<vkUtil::SwapChainFrame>& frames) {

		std::stringstream message;

		for (int i = 0; i < frames.size(); ++i) {

			std::vector<vk::ImageView> attachments = {
				frames[i].imageView
			};

			vk::FramebufferCreateInfo framebufferInfo;
			framebufferInfo.flags = vk::FramebufferCreateFlags();
			framebufferInfo.renderPass = inputChunk.renderpass[pipelineType::SKY];
			framebufferInfo.attachmentCount = attachments.size();
			framebufferInfo.pAttachments = attachments.data();
			framebufferInfo.width = inputChunk.swapchainExtent.width;
			framebufferInfo.height = inputChunk.swapchainExtent.height;
			framebufferInfo.layers = 1;

			try {
				frames[i].framebuffer[pipelineType::SKY] = inputChunk.device.createFramebuffer(framebufferInfo);

				message << "Created sky framebuffer for frame " << i;
				vkLogging::Logger::get_logger()->print(message.str());
				message.str("");
			}
			catch (vk::SystemError err) {
				message << "Failed to create sky framebuffer for frame " << i;
				vkLogging::Logger::get_logger()->print(message.str());
				message.str("");
			}

			attachments.push_back(frames[i].depthBufferView);

			framebufferInfo.renderPass = inputChunk.renderpass[pipelineType::STANDARD];
			framebufferInfo.attachmentCount = attachments.size();
			framebufferInfo.pAttachments = attachments.data();

			try {
				frames[i].framebuffer[pipelineType::STANDARD] = inputChunk.device.createFramebuffer(framebufferInfo);

				message  << "Created standard framebuffer for frame " << i;
				vkLogging::Logger::get_logger()->print(message.str());
				message.str("");
			}
			catch (vk::SystemError err) {
				message << "Failed to create standard framebuffer for frame " << i;
				vkLogging::Logger::get_logger()->print(message.str());
				message.str("");
			}

		}
	}

}