#include <iostream>
#include <thread>

/*
* Threads are typically launched by calling some function,
* but really any callable object can be passed, ie. anything with
* the () operator defined.
*/

struct process {

	//state
	int& i;

	//constructor, initializes state
	process(int& start) : i(start) {

	};

	//the function which will be called when a thread is launched with this struct
	void operator()() {
		for (int j = 0; j < 100; ++j) {
			std::cout << "new thread " << i++ << std::endl;
		}
	}
};

struct background_process {

	//state
	int i;	//taking an int instead of a reference ensures
			//the process is truly independent
	bool& should_exit;	//a reference is ok here, we know the main program will be
						//monitoring this

	//constructor, initializes state
	background_process(int start, bool& flag) : i(start), should_exit(flag) {

	};

	//the function which will be called when a thread is launched with this struct
	void operator()() {
		for (int j = 0; j < 100; ++j) {
			std::cout << "background thread " << i++ << std::endl;
		}
		should_exit = true;
	}
};

void bad_thread_launch() {

	int local_variable = 10;
	//Initialize the struct to launch into
	process counter_process(local_variable);
	std::thread new_thread(counter_process);
	new_thread.detach();
	for (int j = 0; j < 10; ++j) {
		std::cout << "\t\tOriginal thread: " << j++ << std::endl;
	}
	//This function will end before our new thread has done its work.
	//the local variable will be lost.
}

void good_thread_launch() {

	int local_variable = 10;
	//Initialize the struct to launch into
	process counter_process(local_variable);
	std::thread new_thread(counter_process);
	for (int j = 0; j < 100; ++j) {
		std::cout << "\t\tOriginal thread: " << j << std::endl;
	}
	new_thread.join();
	//Wait until the thread has finished its work
}

void good_background_thread(bool& some_state) {

	int local_variable = 10;
	background_process counter_process(local_variable, some_state);
	std::thread new_thread(counter_process);
	new_thread.detach();
	for (int j = 0; j < 1000; ++j) {
		std::cout << "\t\Main thread: " << j++ << std::endl;
	}
	//This function will end before our new thread has done its work.
	//the local variable will be lost.
}

int main() {
	//bad_thread_launch();
	//good_thread_launch();

	bool should_exit = false;
	good_background_thread(should_exit);
	while (!should_exit) {
		//Wait for background process to finish
	}
	return 0;
}