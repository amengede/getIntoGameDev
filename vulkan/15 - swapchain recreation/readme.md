# Swapchain Recreation
Now that we've got things more or less working, we need to make our renderer more robust. OpenGL can handle events like resizing and hiding the window, but in Vulkan we need to do that ourselves.

The basic process is:
* During rendering, errors may be detected.
* If an error is detected, flush out all the pending work, then recreate the invalid resources.

Luckily, dynamic rendering makes this process fairly simple, as only the swapchain needs to be recreated.

## Detecting errors in Rendering
If we go and look at our rendering code, Visual Studio is complaining about us ignoring return values for a number of functions, namely
* waitForFences
* acquireNextImage
* submit
* presentKHR

It's worth looking into each of these to see which sorts of errors they can produce. Specifically, acquireNextImage and present can return  suboptimal and out of date messages. Suboptimal counts as success but indicates the swapchain could benefit from a rebuild. Out of date indicates a failure. In both cases we can rebuild.
```
void Engine::draw() {

	Frame& frame = frames[frameIndex];

	logicalDevice.waitForFences(frame.renderFinishedFence, false, UINT64_MAX);

	auto acquisition = logicalDevice.acquireNextImageKHR(
		swapchain.chain, UINT64_MAX, frame.imageAquiredSemaphore, nullptr);
	vk::Result result = acquisition.result;
	uint32_t imageIndex = acquisition.value;

	if (result == vk::Result::eErrorOutOfDateKHR) {
		// rebuild swapchain
		return;
	}

	logicalDevice.resetFences(frame.renderFinishedFence);

	// graphics

	// presentation

	if (result == vk::Result::eErrorOutOfDateKHR) {
		// rebuild swapchain
		return;
	}

	frameIndex = frameIndex ^ 1;
}
```

## Swapchain Deletion Queue
So how do we actually recreate the swapchain? To start with, as always with Vulkan, we'll refactor the code. We'll give the swapchain its own deletion queue, so that it truly owns its resources.

```
class Swapchain {

// ...

private:

    std::deque<std::function<void(vk::Device)>> deletionQueue;

    // ...
};
```

Upon building, push all deletors onto this queue. Then, we'll add a function to rebuild the swapchain. The function will need to take in all of the arguments of the original build function.

```
void rebuild(
    vk::Device logicalDevice,
    vk::PhysicalDevice physicalDevice,
    vk::SurfaceKHR surface,
    GLFWwindow* window);
```

Its source code is pretty much as you'd expect. Wait, destroy, recreate.

```
void Swapchain::rebuild(
    vk::Device logicalDevice,
    vk::PhysicalDevice physicalDevice,
    vk::SurfaceKHR surface,
    GLFWwindow* window) {

    Logger* logger = Logger::get_logger();
    logger->print("Recreating swapchain!");

    // wait
    logicalDevice.waitIdle();

    // destroy
    while (deletionQueue.size() > 0) {
        deletionQueue.back()(logicalDevice);
        deletionQueue.pop_back();
    }
    images.clear();
    imageViews.clear();

    // recreate
    int width, height;
    glfwGetFramebufferSize(window, &width, &height);
    build(logicalDevice, physicalDevice, surface, width, height);
}
```

Now in the renderer, we can tell the swapchain to rebuild itself! We can enable window resizes in the glfw_backend file and test it out. We have two issues though: the program is crashing upon minimization, and we're getting a bunch of validation errors on program close.
The errors can be fixed by giving the swapchain a destructor.

```
void Swapchain::rebuild(
    vk::Device logicalDevice,
    vk::PhysicalDevice physicalDevice,
    vk::SurfaceKHR surface,
    GLFWwindow* window) {

    Logger* logger = Logger::get_logger();
    logger->print("Recreating swapchain!");

    // wait
    logicalDevice.waitIdle();

    destroy(logicalDevice);

    // recreate
    int width, height;
    glfwGetFramebufferSize(window, &width, &height);
    build(logicalDevice, physicalDevice, surface, width, height);
}

void Swapchain::destroy(vk::Device logicalDevice) {

    while (deletionQueue.size() > 0) {
        deletionQueue.back()(logicalDevice);
        deletionQueue.pop_back();
    }
    images.clear();
    imageViews.clear();
}
```

This destructor can be called from the renderer also.

## Minimizing
The issue with minimizing is that the window basically gets resized to a zero size. The code will try to create a swapchain with size zero images. We could handle this with glfw callbacks or some sort of message passing protocol between the main and render threads, but that might be a good topic for a future tutorial (I want to do it justice with ringbuffers). For now, we can hack it. Give the swapchain a variable to track whether it's outdated.

```
bool outdated = false;
```

```
void Swapchain::build(
    vk::Device logicalDevice, vk::PhysicalDevice physicalDevice, 
    vk::SurfaceKHR surface, uint32_t width, uint32_t height) {

    // ...

    outdated = false;
}
```

Now if our code detects an error, it simply tells the swapchain it's outdated and returns.
At the top of the render function, we first manually check if the window is minimised, if the window is not minimized, we then check if the swapchain is outdated, and if it is then rebuild and continue.

```
void Engine::draw() {

	int width, height;
	glfwGetFramebufferSize(window, &width, &height);

	if (width == 0 && height == 0) {
		swapchain.outdated = true;
		return;
	}

	if (swapchain.outdated) {
		swapchain.rebuild(logicalDevice, physicalDevice, surface, window);
	}

	// ...

	if (result == vk::Result::eErrorOutOfDateKHR) {
		swapchain.outdated = true;
		return;
	}

	// ...

	if (result == vk::Result::eErrorOutOfDateKHR) {
		swapchain.outdated = true;
		return;
	}

	frameIndex = frameIndex ^ 1;
}
```

There we have it! Hopefully the code is now working and resizing nicely.