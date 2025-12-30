#pragma once
#include "job.h"

namespace vkJob {
	class WorkerThread {
	public:
		bool& done;
		WorkQueue& workQueue;
		vk::CommandBuffer commandBuffer;
		vk::Queue queue;

		WorkerThread(WorkQueue& workQueue, bool& done, vk::CommandBuffer commandBuffer, vk::Queue queue);

		void operator()();
	};
}