#pragma once
#include "config.h"
#include "frame.h"

namespace vkInit {

	/**
		Data structures involved in making framebuffers for the
		swapchain.
	*/
	struct framebufferInput {
		vk::Device device;
		vk::RenderPass renderpass;
		vk::Extent2D swapchainExtent;
	};

	/**
		Make framebuffers for the swapchain

		\param inputChunk required input for creation
		\param frames the vector to be populated with the created framebuffers
		\param debug whether the system is running in debug mode.
	*/
	void make_framebuffers(framebufferInput inputChunk, std::vector<vkUtil::SwapChainFrame>& frames, bool debug) {

		for (int i = 0; i < frames.size(); ++i) {

			std::vector<vk::ImageView> attachments = {
				frames[i].imageView
			};

			vk::FramebufferCreateInfo framebufferInfo;
			framebufferInfo.flags = vk::FramebufferCreateFlags();
			framebufferInfo.renderPass = inputChunk.renderpass;
			framebufferInfo.attachmentCount = attachments.size();
			framebufferInfo.pAttachments = attachments.data();
			framebufferInfo.width = inputChunk.swapchainExtent.width;
			framebufferInfo.height = inputChunk.swapchainExtent.height;
			framebufferInfo.layers = 1;

			try {
				frames[i].framebuffer = inputChunk.device.createFramebuffer(framebufferInfo);

				if (debug) {
					std::cout << "Created framebuffer for frame " << i << std::endl;
				}
			}
			catch (vk::SystemError err) {
				if (debug) {
					std::cout << "Failed to create framebuffer for frame " << i << std::endl;
				}
			}

		}
	}

}