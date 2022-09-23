#include <glad/glad.h>
#include <GLFW/glfw3.h>
#include <iostream>
#include <vector>
#include <thread>
#include <sstream>

class Engine {
public:
	GLFWwindow* window;
	Engine(bool& flag)
	: done(flag) {
	}

	void operator()() {
		window = makeWindow();
		double lastTime = glfwGetTime();
		double currentTime = 0.0;
		int numFrames = 0;
		makeTriangle();
		shader = makeProgram();
		glUseProgram(shader);
		glClearColor(0.5f, 0.1f, 0.3f, 1.0f);
		glClear(GL_COLOR_BUFFER_BIT);
		while (!glfwWindowShouldClose(window)) {

			//processInput();

			//glfwPollEvents();

			//draw triangle
			glClear(GL_COLOR_BUFFER_BIT);
			glUseProgram(shader);
			glBindVertexArray(VAO);
			glDrawArrays(GL_TRIANGLES, 0, vertexCount);

			currentTime = glfwGetTime();
			double delta = currentTime - lastTime;

			if (delta >= 1) {
				int framerate{ std::max(1, int(numFrames / delta)) };
				std::stringstream title;
				title << "Running at " << framerate << " fps.";
				glfwSetWindowTitle(window, title.str().c_str());
				lastTime = currentTime;
				numFrames = -1;
			}

			++numFrames;

			glFlush();
			//glfwSwapBuffers(window);

		}

		//free memory
		glDeleteBuffers(1, &VBO);
		glDeleteVertexArrays(1, &VAO);
		glDeleteProgram(shader);

		glfwTerminate();
	}

private:
	bool& done;
	double lastTime;
	double currentTime;
	int numFrames;
	unsigned int shader;
	int vertexCount;
	unsigned int VBO, VAO;
	std::vector<float> vertices;

	unsigned int makeProgram() {
		//make the shaders, we'll hardcode everything, for now

		//     \0 is the nul character, used to indicate the end of a string.
		const char* vertexShaderSource = "#version 450 core\n"
			"layout (location = 0) in vec3 vertexPosition;\n"
			"layout (location = 1) in vec3 vertexColor;\n"
			"layout (location = 0) out vec3 fragmentColor;\n"
			"void main()\n"
			"{\n"
			"    gl_Position = vec4(vertexPosition, 1.0);\n"
			"    fragmentColor = vertexColor;\n"
			"}\0";

		const char* fragmentShaderSource = "#version 450 core\n"
			"layout (location = 0) in vec3 fragmentColor;\n"
			"out vec4 finalColor;\n"
			"void main()\n"
			"{\n"
			"    finalColor = vec4(fragmentColor, 1.0);\n"
			"}\0";

		//compile the shaders
		unsigned int vertexShader = glCreateShader(GL_VERTEX_SHADER);
		//last argument is length NULL indicates that the string is NUL-terminated
		glShaderSource(vertexShader, 1, &vertexShaderSource, NULL);
		glCompileShader(vertexShader);

		//check error status
		int success;
		char errorLog[1024];
		glGetShaderiv(vertexShader, GL_COMPILE_STATUS, &success);
		if (!success) {
			glGetShaderInfoLog(vertexShader, 1024, NULL, errorLog);
			std::cout << "Vertex Shader compilation error:\n" << errorLog << '\n';
		}

		unsigned int fragmentShader = glCreateShader(GL_FRAGMENT_SHADER);
		//last argument is length NULL indicates that the string is NUL-terminated
		glShaderSource(fragmentShader, 1, &fragmentShaderSource, NULL);
		glCompileShader(fragmentShader);

		//check error status
		glGetShaderiv(fragmentShader, GL_COMPILE_STATUS, &success);
		if (!success) {
			glGetShaderInfoLog(fragmentShader, 1024, NULL, errorLog);
			std::cout << "fragment Shader compilation error:\n" << errorLog << '\n';
		}

		//link shaders together to form a program, this will run on our GPU to draw stuff
		unsigned int shader = glCreateProgram();
		glAttachShader(shader, vertexShader);
		glAttachShader(shader, fragmentShader);
		glLinkProgram(shader);

		//check error status
		glGetProgramiv(shader, GL_LINK_STATUS, &success);
		if (!success) {
			glGetProgramInfoLog(shader, 1024, NULL, errorLog);
			std::cout << "Shader linking error:\n" << errorLog << '\n';
		}

		//memory was allocated to load source code and compile the shaders,
		//but they aren't needed anymore
		glDeleteShader(vertexShader);
		glDeleteShader(fragmentShader);

		return shader;
	}

	void makeTriangle() {
		// x,y,z,r,g,b
		vertices = { {
				-0.25f, -0.25f, 0.0f, 1.0f, 0.0f, 0.0f,
				 0.25f, -0.25f, 0.0f, 0.0f, 1.0f, 0.0f,
				 0.0f,  0.25f, 0.0f, 0.0f, 0.0f, 1.0f
		} };

		vertexCount = 3;

		glCreateBuffers(1, &VBO);

		glCreateVertexArrays(1, &VAO);
		glVertexArrayVertexBuffer(VAO, 0, VBO, 0, 6 * sizeof(float));

		glNamedBufferStorage(VBO, vertices.size() * sizeof(float), vertices.data(), GL_DYNAMIC_STORAGE_BIT);

		glEnableVertexArrayAttrib(VAO, 0);
		glEnableVertexArrayAttrib(VAO, 1);
		//(VAO, location, size, type, should be normalized, (void*)offset)
		glVertexArrayAttribFormat(VAO, 0, 3, GL_FLOAT, GL_FALSE, 0);
		glVertexArrayAttribFormat(VAO, 1, 3, GL_FLOAT, GL_FALSE, 3 * sizeof(float));
		//(VAO, location, binding)
		glVertexArrayAttribBinding(VAO, 0, 0);
		glVertexArrayAttribBinding(VAO, 1, 0);
	}

	GLFWwindow* makeWindow() {
		if (!glfwInit()) {
			throw std::runtime_error("Failed to make window");
		}

		glfwWindowHint(GLFW_CONTEXT_VERSION_MAJOR, 4);
		glfwWindowHint(GLFW_CONTEXT_VERSION_MINOR, 5);
		glfwWindowHint(GLFW_OPENGL_PROFILE, GLFW_OPENGL_CORE_PROFILE);
		glfwWindowHint(GLFW_DOUBLEBUFFER, GLFW_FALSE);

		GLFWwindow* window = glfwCreateWindow(640, 480, "This is working I hope", NULL, NULL);
		if (!window) {
			std::cout << "Window creation failed\n";
			return NULL;
		}
		glfwMakeContextCurrent(window);

		if (!gladLoadGLLoader((GLADloadproc)glfwGetProcAddress)) {
			std::cout << "GLAD initialization failed\n";
			return NULL;
		}

		glViewport(0, 0, 640, 480);

		return window;
	}

	void processInputThread() {

		if (glfwGetKey(window, GLFW_KEY_ESCAPE) == GLFW_PRESS) {
			std::cout << "------Escape!------" << std::endl;
			glfwSetWindowShouldClose(window, true);
		}
	}

};

void processInput(GLFWwindow* window) {

	if (glfwGetKey(window, GLFW_KEY_ESCAPE) == GLFW_PRESS) {
		std::cout << "------Escape!------" << std::endl;
		glfwSetWindowShouldClose(window, true);
	}
}

int main() {
	
	bool engineRunning = true;

	Engine renderer(engineRunning);

	std::thread render_loop(renderer);
	render_loop.detach();
	while (!renderer.window) {
		//wait
	}
	GLFWwindow* window = renderer.window;
	//glfwMakeContextCurrent(NULL);

	//game loop
	
	while (!glfwWindowShouldClose(window)) {

		processInput(window);

		glfwPollEvents();

	}
	
	while (engineRunning) {
		//wait
	}

	return 0;
}