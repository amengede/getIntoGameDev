#pragma once
#include "../../config.h"
namespace vkUtil {

	/**
		Begin recording a command buffer intended for a single submit.
	*/
	void startJob(vk::CommandBuffer commandBuffer);

	/**
		Finish recording a command buffer and submit it.
	*/
	void endJob(vk::CommandBuffer commandBuffer, vk::Queue submissionQueue);
}