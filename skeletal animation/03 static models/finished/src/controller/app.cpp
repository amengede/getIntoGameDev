#include "app.h"

App::App() {
    set_up_glfw();
}

App::~App() {

	for (unsigned int& shader : shaders) {
    	glDeleteProgram(shader);
	}

    delete motionSystem;
    delete renderSystem;
    
    glfwTerminate();
}

void App::run() {

	lastTime = glfwGetTime();
	numFrames = 0;
	frameTime = 16.0f;

    while (!glfwWindowShouldClose(window)) {

        motionSystem->update(frameTime/1000.0f);
		renderSystem->update();
		
		handle_frame_timing();
	}
}

void App::set_up_glfw() {

    glfwInit();
	glfwWindowHint(GLFW_CONTEXT_VERSION_MAJOR, 3);
	glfwWindowHint(GLFW_CONTEXT_VERSION_MINOR, 3);
	glfwWindowHint(GLFW_OPENGL_PROFILE, GLFW_OPENGL_CORE_PROFILE);
	glfwWindowHint(GLFW_OPENGL_FORWARD_COMPAT, GLFW_TRUE);
	
	window = glfwCreateWindow(640, 480, "Hello Window!", NULL, NULL);
	glfwMakeContextCurrent(window);
	glfwSwapInterval(0);

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

	glEnable(GL_DEPTH_TEST);
	glDepthFunc(GL_LESS);
	glEnable(GL_CULL_FACE);
    glCullFace(GL_BACK);

	shaders.push_back(make_shader(
		"src/shaders/vertex.txt", 
		"src/shaders/fragment.txt"));
    
	glm::mat4 projection = glm::perspective(
		45.0f, 640.0f / 480.0f, 0.1f, 50.0f);

	unsigned int shader = shaders[0];
    glUseProgram(shader);
	unsigned int projLocation = glGetUniformLocation(shader, "projection");
	glUniformMatrix4fv(projLocation, 1, GL_FALSE, glm::value_ptr(projection));
}

void App::make_systems() {
    motionSystem = new MotionSystem(transformComponents, physicsComponents);
    renderSystem = new RenderSystem(shaders, window, transformComponents, 
		renderComponents);
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