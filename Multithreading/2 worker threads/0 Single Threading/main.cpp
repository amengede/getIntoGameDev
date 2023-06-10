#include <iostream>
#include <vector>
#include <chrono>

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
		std::cout << "Job " << id << " completed" << std::endl;
		status = JobStatus::COMPLETE;
	}
};

class WorkQueue {
public:
	Job* first = nullptr, * last = nullptr;

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

int main() {

	unsigned int jobsDispatched{ 0 };
	int newJobCount{ 0 };
	WorkQueue workQueue;

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

		while (!workQueue.done()) {
			workQueue.get_next()->execute();
		}

		auto end = std::chrono::high_resolution_clock::now();
		std::cout << "Work finished in " << std::chrono::duration_cast<std::chrono::milliseconds>(end - start).count() << " ms" << std::endl;
		workQueue.clear();


	}

	std::cout << "Goodbye see you!" << std::endl;
	return 0;
}