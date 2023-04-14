#include "worker_thread.h"

vkJob::WorkerThread::WorkerThread(WorkQueue& workQueue, bool& done, vk::CommandBuffer commandBuffer, vk::Queue queue):
workQueue(workQueue), done(done){
	this->commandBuffer = commandBuffer;
	this->queue = queue;
}

void vkJob::WorkerThread::operator()() {

	workQueue.lock.lock();
	std::cout << "----    Thread is ready to go.    ----" << std::endl;
	workQueue.lock.unlock();

	while (!done) {

		if (!workQueue.lock.try_lock()) {
			std::this_thread::sleep_for(std::chrono::milliseconds(200));
			continue;
		}
		
		if (workQueue.done()) {
			workQueue.lock.unlock();
			continue;
		}

		vkJob::Job* pendingJob = workQueue.get_next();

		if (!pendingJob) {
			workQueue.lock.unlock();
			continue;
		}
		std::cout << "----    Working on a job.    ----" << std::endl;
		pendingJob->status = JobStatus::IN_PROGRESS;
		workQueue.lock.unlock();
		pendingJob->execute(commandBuffer, queue);
	}

	std::cout << "----    Thread done.    ----" << std::endl;
}