#pragma once
#include "config.h"

namespace vkUtil {

	/**
		Holds the data structures associated with a "Frame"
	*/
	struct SwapChainFrame {
		vk::Image image;
		vk::ImageView imageView;
	};

}