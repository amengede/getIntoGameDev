#include "app.h"
#include "../factories/texture_factory.h"

App::App() {
    set_up_glfw();
}

App::~App() {

	for (unsigned int& shader : shaders) {
    	glDeleteProgram(shader);
	}
	glDeleteTextures(1, &colorbuffer);

    delete cameraSystem;
    delete renderSystem;
    
    glfwTerminate();
}

void App::run() {

	lastTime = glfwGetTime();
	numFrames = 0;
	frameTime = 16.0f;

    while (!glfwWindowShouldClose(window)) {

        bool should_close = cameraSystem->update(frameTime/1000.0f);
		if (should_close) {
			break;
		}

		renderSystem->update();

		glfwSwapBuffers(window);

		
		handle_frame_timing();
	}
}

void App::set_up_glfw() {

    glfwInit();
	glfwWindowHint(GLFW_CONTEXT_VERSION_MAJOR, 4);
	glfwWindowHint(GLFW_CONTEXT_VERSION_MINOR, 3);
	glfwWindowHint(GLFW_OPENGL_PROFILE, GLFW_OPENGL_CORE_PROFILE);
	glfwWindowHint(GLFW_OPENGL_FORWARD_COMPAT, GLFW_TRUE);
	
	window = glfwCreateWindow(640, 480, "Hello Window!", NULL, NULL);
	glfwMakeContextCurrent(window);
	glfwSwapInterval(0);
	glfwSetInputMode(window, GLFW_CURSOR, GLFW_CURSOR_HIDDEN);

    if (!gladLoadGLLoader((GLADloadproc)glfwGetProcAddress)) {
		std::cout << "Couldn't load opengl" << std::endl;
		glfwTerminate();
	}

}

void App::set_up_opengl() {

    glClearColor(0.25f, 0.5f, 0.75f, 1.0f);
	//Set the rendering region to the actual screen size
	int w,h;
	glfwGetFramebufferSize(window, &w, &h);
	//(left, top, width, height)
	glViewport(0,0,w,h);

	glDisable(GL_DEPTH_TEST);

	shaders.push_back(make_shader(
		"../../src/shaders/vertex.txt", 
		"../../src/shaders/fragment.txt"));

	TextureFactory factory;
	colorbuffer = factory.build_colorbuffer(window);
}

void App::make_systems() {
    cameraSystem = new CameraSystem(shaders, window, cameraComponents);
    renderSystem = new RenderSystem(shaders, colorbuffer);
}

void App::handle_frame_timing() {
	currentTime = glfwGetTime();
	double delta = currentTime - lastTime;

	if (delta >= 1) {
		int framerate{ std::max(1, int(numFrames / delta)) };
		std::stringstream title;
		title << "Running at " << framerate << " fps.";
		glfwSetWindowTitle(window, title.str().c_str());
		lastTime = currentTime;
		numFrames = -1;
		frameTime = float(1000.0 / framerate);
	}

	++numFrames;
}