#include "app.h"

App::App() {
    set_up_glfw();
}

App::~App() {

	for (unsigned int& shader : shaders) {
    	glDeleteProgram(shader);
	}

    delete renderSystem;
    
    glfwTerminate();
}

void App::run() {

	lastTime = glfwGetTime();
	numFrames = 0;
	frameTime = 16.0f;

    while (!glfwWindowShouldClose(window)) {

		glfwPollEvents();
		animationSystem->update();
		skeletalSystem->update();
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
	//glfwSwapInterval(0);

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
	glEnable(GL_PROGRAM_POINT_SIZE);

	shaders.push_back(make_shader(
		"src/shaders/vertex.txt", 
		"src/shaders/fragment.txt"));
	shaders.push_back(make_shader(
		"src/shaders/bone_vertex.txt",
		"src/shaders/bone_fragment.txt"));

	glm::mat4 projection = glm::perspective(glm::radians(22.5f), 640.0f / 480.0f, 0.1f, 50.0f);

	for (unsigned int shader : shaders) {
		glUseProgram(shader);
		glUniformMatrix4fv(
			glGetUniformLocation(shader, "projection"),
			1, GL_FALSE, glm::value_ptr(projection));
	}
}

void App::make_systems() {
	animationSystem = new AnimationSystem(animationSet, animations, skeletons);
    renderSystem = new RenderSystem(shaders, window, transformComponents, 
		renderComponents, skeletons);
	skeletalSystem = new SkeletalSystem(skeletons);
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