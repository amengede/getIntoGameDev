#include <iostream>
#include <thread>
#include <vector>
#include <chrono>
#include <mutex>

enum class JobStatus {
	PENDING,
	IN_PROGRESS,
	COMPLETE
};

class Job {
public:
	JobStatus status = JobStatus::PENDING;
	Job* next = nullptr;
	virtual void execute() = 0;
};

class LoudJob : public Job {
public:
	unsigned int id;

	LoudJob(unsigned int id) {
		this->id = id;
	}

	virtual void execute() final {
		std::cout << "Job " << id << " completed";
		status = JobStatus::COMPLETE;
	}
};

class WorkQueue {
public:
	Job* first = nullptr, * last = nullptr;
	std::mutex lock, logLock;

	void add(Job* job) {

		if (!first) {
			first = job;
			last = job;
		}
		else {
			last->next = job;
			last = job;
		}

	}

	Job* get_next() {

		Job* current = first;
		while (current) {
			if (current->status == JobStatus::PENDING) {
				return current;
			}

			current = current->next;
		}

		return nullptr;
	}

	bool done() {

		Job* current = first;
		while (current) {
			if (current->status != JobStatus::COMPLETE) {
				return false;
			}

			current = current->next;
		}

		return true;
	}

	void clear() {

		Job* current = first;
		while (current) {

			Job* previous = current;
			current = current->next;
			delete previous;

		}

		first = nullptr;
		last = nullptr;
	}
};

class WorkerThread {
public:
	bool& done;
	WorkQueue& workQueue;
	unsigned int id;

	WorkerThread(WorkQueue& workQueue, bool& done, unsigned int id) :
		workQueue(workQueue), done(done) {

		this->id = id;
	}

	void operator()() {

		workQueue.logLock.lock();
		std::cout << "----    Thread " << id << " started.    ----" << std::endl;
		workQueue.logLock.unlock();

		//Keep spinning wheels indefinitely
		while (!done) {

			//Try get access to the queue
			if (!workQueue.lock.try_lock()) {
				//This might reduce power consumption a little
				//std::this_thread::sleep_for(std::chrono::milliseconds(200));
				continue;
			}

			if (workQueue.done()) {
				//We have access to the queue, but it has no work for us to do.
				workQueue.lock.unlock();
				continue;
			}


			Job* pendingJob{ workQueue.get_next() };

			//never hurts to check this
			if (!pendingJob) {
				workQueue.lock.unlock();
				continue;
			}

			pendingJob->status = JobStatus::IN_PROGRESS;
			workQueue.lock.unlock();

			workQueue.logLock.lock();
			pendingJob->execute();
			std::cout << " by thread " << id << std::endl;
			workQueue.logLock.unlock();
		}

		workQueue.logLock.lock();
		std::cout << "----    Thread " << id << " done.    ----" << std::endl;
		workQueue.logLock.unlock();
	}
};

int main() {

	unsigned int jobsDispatched{ 0 };
	int newJobCount{ 0 };
	size_t threadCount{ std::thread::hardware_concurrency() - 1 };
	WorkQueue workQueue;
	std::vector<std::thread> workerThreads;
	bool done{ false };

	workerThreads.reserve(threadCount);
	for (size_t i = 0; i < threadCount; ++i) {
		workerThreads.push_back(
			std::thread(
				WorkerThread(workQueue, done, i)
			)
		);
	}

	while (true) {

		std::cout << "How many jobs should we launch (-ve: exit program)?: ";
		std::cin >> newJobCount;

		auto start = std::chrono::high_resolution_clock::now();
		if (newJobCount < 0) {
			break;
		}
		else {
			while (newJobCount > 0) {
				workQueue.add(new LoudJob(jobsDispatched++));
				newJobCount--;
			}
		}

		while (true) {

			if (!workQueue.lock.try_lock()) {
				//std::this_thread::sleep_for(std::chrono::milliseconds(200));
				continue;
			}

			if (workQueue.done()) {
				auto end = std::chrono::high_resolution_clock::now();
				std::cout << "Work finished in " << std::chrono::duration_cast<std::chrono::milliseconds>(end - start).count() << " ms" << std::endl;
				workQueue.clear();
				workQueue.lock.unlock();
				break;
			}
			workQueue.lock.unlock();
		}

	}

	done = true;

	for (size_t i = 0; i < threadCount; ++i) {
		workerThreads[i].join();
	}

	std::cout << "Threads ended successfully." << std::endl;
	workQueue.clear();

	std::cout << "Goodbye see you!" << std::endl;
	return 0;
}