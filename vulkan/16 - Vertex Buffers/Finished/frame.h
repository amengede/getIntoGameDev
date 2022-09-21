#pragma once
#include "config.h"

namespace vkUtil {

	/**
	* Holds various objects used on a per frame basis
	* 
	* image:			The image to render to
	* imageView:		View to the actual image (all access to vulkan images is through imageviews)
	* frameBuffer:		Framebuffer to this frame, describes attachments
	* commandBuffer:	Drawing commands to this frame are recorded here
	* imageAvailable:	This semaphore is unavailable while the frame 
						image is being acquired
	* imageFinished:	This semaphore is unavailable while the frame is being rendered to
	* inFlight:			This fence is unsignalled while the frame is being acquired and rendered. 
						After being reset, the frame can be reset before presentation.
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