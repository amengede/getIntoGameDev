#pragma once
#include "../../config.h"

namespace vkUtil {

	/**
		Holds the data structures associated with a "Frame"
	*/
	struct SwapChainFrame {
		vk::Image image;
		vk::ImageView imageView;
		vk::Framebuffer framebuffer;
		vk::CommandBuffer commandBuffer;
		vk::Semaphore imageAvailable, renderFinished;
		vk::Fence inFlight;
	};

}