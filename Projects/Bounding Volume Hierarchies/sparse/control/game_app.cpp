#include "game_app.h"

GameApp::GameApp(GameAppCreateInfo* createInfo) {
	this->width = createInfo->width;
	this->height = createInfo->height;

	lastTime = glfwGetTime();
	numFrames = 0;
	frameTime = 16.0f;

	window = makeWindow();
	glfwSetInputMode(window, GLFW_CURSOR, GLFW_CURSOR_HIDDEN);

	renderer = new Engine(width, height);
	scene = new Scene();

	mainLoop();
}

GLFWwindow* GameApp::makeWindow() {
	glfwInit();

	glfwWindowHint(GLFW_CONTEXT_VERSION_MAJOR, 4);
	glfwWindowHint(GLFW_CONTEXT_VERSION_MINOR, 5);
	glfwWindowHint(GLFW_OPENGL_PROFILE, GLFW_OPENGL_CORE_PROFILE);
	glfwWindowHint(GLFW_DOUBLEBUFFER, GLFW_FALSE);

	GLFWwindow* window = glfwCreateWindow(width, height, "This is working I hope", NULL, NULL);

	glfwMakeContextCurrent(window);

	if (!gladLoadGLLoader((GLADloadproc)glfwGetProcAddress)) {
		std::cout << "GLAD initialization failed\n";
		return NULL;
	}

	glViewport(0, 0, width, height);

	return window;
}

returnCode GameApp::processInput() {
	
	int wasdState{ 0 };
	float walk_direction{ scene->player->eulers.z };
	bool walking{ false };

	if (glfwGetKey(window, GLFW_KEY_W) == GLFW_PRESS) {
		wasdState += 1;
	}

	if (glfwGetKey(window, GLFW_KEY_A) == GLFW_PRESS) {
		wasdState += 2;
	}

	if (glfwGetKey(window, GLFW_KEY_S) == GLFW_PRESS) {
		wasdState += 4;
	}

	if (glfwGetKey(window, GLFW_KEY_D) == GLFW_PRESS) {
		wasdState += 8;
	}

	switch (wasdState) {
	case 1:
	case 11:
		//forwards
		walking = true;
		break;
	case 3:
		//left-forwards
		walking = true;
		walk_direction += 45;
		break;
	case 2:
	case 7:
		//left
		walking = true;
		walk_direction += 90;
		break;
	case 6:
		//left-backwards
		walking = true;
		walk_direction += 135;
		break;
	case 4:
	case 14:
		//backwards
		walking = true;
		walk_direction += 180;
		break;
	case 12:
		//right-backwards
		walking = true;
		walk_direction += 225;
		break;
	case 8:
	case 13:
		//right
		walking = true;
		walk_direction += 270;
		break;
	case 9:
		//right-forwards
		walking = true;
		walk_direction += 315;
	}

	if (walking) {
		scene->movePlayer(
			0.1f * frameTime / 16.0f * glm::vec3{
				glm::cos(glm::radians(walk_direction)),
				glm::sin(glm::radians(walk_direction)),
				0.0f
			}
		);
	}

	double mouse_x, mouse_y;
	glfwGetCursorPos(window, &mouse_x, &mouse_y);
	glfwSetCursorPos(window, static_cast<double>(width / 2), static_cast<double>(height / 2));

	float delta_x{ static_cast<float>(mouse_x - static_cast<double>(width / 2)) };
	float delta_y{ static_cast<float>(mouse_y - static_cast<double>(height / 2)) };

	scene->spinPlayer(
		frameTime / 16.0f * 0.1f * glm::vec3{
			0.0f, delta_y, -delta_x
		}
	);
	
	if (glfwGetKey(window, GLFW_KEY_ESCAPE) == GLFW_PRESS) {
		return returnCode::QUIT;
	}
	return returnCode::CONTINUE;
}

void GameApp::mainLoop() {

	returnCode nextAction = returnCode::CONTINUE;

	while (nextAction == returnCode::CONTINUE) {
		
		nextAction = processInput();
		glfwPollEvents();

		//update
		scene->update(frameTime / 16.0f);

		//draw
		renderer->render(scene);
		renderer->draw_screen();

		calculateFrameRate();

	}
}

GameApp::~GameApp() {
	//free memory
	delete scene;
	delete renderer;
	glfwTerminate();
}

void GameApp::calculateFrameRate() {
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
		renderer->adapt_framerate(framerate);
	}

	++numFrames;
}