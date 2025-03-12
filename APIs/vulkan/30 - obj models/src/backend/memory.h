/*---------------------------------------------------------------------------*/
/*	Memory Management functions
/*---------------------------------------------------------------------------*/
#pragma once
#include <vma/vk_mem_alloc.h>
#include <deque>
#include <functional>

enum class AllocatorScope {
	eFrame,
	eProgram
};

namespace mem {

	struct Allocator {
		VmaAllocator allocator = nullptr;
		VmaPool pool = nullptr;
		std::deque<std::function<void(VmaAllocator)>> deletionQueue;

		void free() {

			if (pool) {
				vmaDestroyPool(allocator, pool);
			}
			vmaDestroyAllocator(allocator);
		}

		void flush_deletion_queue() {

			while (deletionQueue.size() > 0) {
				deletionQueue.back()(allocator);
				deletionQueue.pop_back();
			}
		}
	};

	/**
	* @brief bundle of info used for creating memory pools
	*/
	struct ImagePoolCreateInfo {
		VmaAllocator allocator;
		VkImageUsageFlags usage;
		bool hostWrite = false;
		bool freeAtOnce = true;
		VkDeviceSize blockSize;
		size_t blockCount = 0;
		VkDeviceSize alignment = 0;
	};

	/**
	* @brief create a memory pool, intended for image allocation
	*/
	VmaPool create_pool(const ImagePoolCreateInfo& imagePoolInfo);
}
/*---------------------------------------------------------------------------*/