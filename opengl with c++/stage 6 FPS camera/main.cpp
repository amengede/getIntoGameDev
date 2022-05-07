#include <glad/glad.h>
#include <GLFW/glfw3.h>
#include <iostream>
#include <vector>
#define STB_IMAGE_IMPLEMENTATION
#include "stb_image.h"
#include <glm/glm.hpp>
//for transformations:
#include <glm/gtc/matrix_transform.hpp>
//to pass matrices to the shader
#include <glm/gtc/type_ptr.hpp>

GLFWwindow* initialize(int width, int height) {
	glfwInit();

	glfwWindowHint(GLFW_CONTEXT_VERSION_MAJOR, 4);
	glfwWindowHint(GLFW_CONTEXT_VERSION_MINOR, 5);
	glfwWindowHint(GLFW_OPENGL_PROFILE, GLFW_OPENGL_CORE_PROFILE);

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

void processInput(GLFWwindow* window, glm::vec3& playerPosition, glm::vec3& playerEulers) {

	int wasdState{ 0 };
	float walk_direction{ playerEulers.z };
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
		playerPosition += 0.1f * glm::vec3{
			glm::cos(glm::radians(walk_direction)),
			glm::sin(glm::radians(walk_direction)),
			0.0f
		};
	}

	double mouse_x, mouse_y;
	glfwGetCursorPos(window, &mouse_x, &mouse_y);
	glfwSetCursorPos(window, static_cast<double>(640 / 2), static_cast<double>(480 / 2));

	float delta_x{ static_cast<float>(mouse_x - static_cast<double>(640 / 2)) };
	playerEulers.z -= delta_x;

	float delta_y{ static_cast<float>(mouse_y - static_cast<double>(480 / 2)) };
	playerEulers.y = std::max(std::min(playerEulers.y + delta_y, 180.0f), 0.0f);

	if (glfwGetKey(window, GLFW_KEY_ESCAPE) == GLFW_PRESS) {
		glfwSetWindowShouldClose(window, true);
	}
}

unsigned int makeProgram() {
	const char* vertexShaderSource = "#version 450 core\n"
		"layout (location = 0) in vec3 vertexPosition;\n"
		"layout (location = 1) in vec2 vertexTexCoords;\n"
		"layout (location = 0) out vec2 fragmentTexCoords;\n"
		"uniform mat4 model;\n"
		"uniform mat4 view;\n"
		"uniform mat4 projection;\n"
		"void main()\n"
		"{\n"
		"    gl_Position = projection * view * model * vec4(vertexPosition, 1.0);\n"
		"    fragmentTexCoords = vec2(vertexTexCoords.x, 1.0 - vertexTexCoords.y);\n"
		"}\0";

	const char* fragmentShaderSource = "#version 450 core\n"
		"layout (location = 0) in vec2 fragmentTexCoords;\n"
		"uniform sampler2D basicTexture;\n"
		"out vec4 finalColor;\n"
		"void main()\n"
		"{\n"
		"    finalColor = texture(basicTexture, fragmentTexCoords);\n"
		"}\0";

	unsigned int vertexShader = glCreateShader(GL_VERTEX_SHADER);
	glShaderSource(vertexShader, 1, &vertexShaderSource, NULL);
	glCompileShader(vertexShader);

	int success;
	char errorLog[1024];
	glGetShaderiv(vertexShader, GL_COMPILE_STATUS, &success);
	if (!success) {
		glGetShaderInfoLog(vertexShader, 1024, NULL, errorLog);
		std::cout << "Vertex Shader compilation error:\n" << errorLog << '\n';
	}

	unsigned int fragmentShader = glCreateShader(GL_FRAGMENT_SHADER);
	glShaderSource(fragmentShader, 1, &fragmentShaderSource, NULL);
	glCompileShader(fragmentShader);

	glGetShaderiv(fragmentShader, GL_COMPILE_STATUS, &success);
	if (!success) {
		glGetShaderInfoLog(fragmentShader, 1024, NULL, errorLog);
		std::cout << "fragment Shader compilation error:\n" << errorLog << '\n';
	}

	unsigned int shader = glCreateProgram();
	glAttachShader(shader, vertexShader);
	glAttachShader(shader, fragmentShader);
	glLinkProgram(shader);

	glGetProgramiv(shader, GL_LINK_STATUS, &success);
	if (!success) {
		glGetProgramInfoLog(shader, 1024, NULL, errorLog);
		std::cout << "Shader linking error:\n" << errorLog << '\n';
	}

	glDeleteShader(vertexShader);
	glDeleteShader(fragmentShader);

	return shader;
}

int main() {

	glm::vec3 playerPosition = { 0.0f, 0.0f, 1.0f };
	glm::vec3 playerEulers = { 0.0f, 90.0f,0.0f };

	int width = 640;
	int height = 480;
	float aspectRatio = (float)width / float(height);
	GLFWwindow* window = initialize(width, height);
	if (!window) {
		glfwTerminate();
		return -1;
	}
	glfwSetInputMode(window, GLFW_CURSOR, GLFW_CURSOR_HIDDEN);

	unsigned int shader = makeProgram(); 
	glUseProgram(shader);

	//Make Cube
	//x,y,z,s,t
	std::vector<float> vertices = { {
			-0.5f, -0.5f, -0.5f, 0.0f, 0.0f, // bottom
			 0.5f, -0.5f, -0.5f, 1.0f, 0.0f,
			 0.5f,  0.5f, -0.5f, 1.0f, 1.0f,

			 0.5f,  0.5f, -0.5f, 1.0f, 1,
			-0.5f,  0.5f, -0.5f, 0.0f, 1,
			-0.5f, -0.5f, -0.5f, 0.0f, 0,

			-0.5f, -0.5f,  0.5f, 0.0f, 0.0f, //top
			 0.5f, -0.5f,  0.5f, 1.0f, 0.0f,
			 0.5f,  0.5f,  0.5f, 1.0f, 1.0f,

			 0.5f,  0.5f,  0.5f, 1.0f, 1.0f,
			-0.5f,  0.5f,  0.5f, 0.0f, 1.0f,
			-0.5f, -0.5f,  0.5f, 0.0f, 0.0f,

			-0.5f,  0.5f,  0.5f, 1.0f, 0.0f, //left
			-0.5f,  0.5f, -0.5f, 1.0f, 1.0f,
			-0.5f, -0.5f, -0.5f, 0.0f, 1.0f,

			-0.5f, -0.5f, -0.5f, 0.0f, 1.0f,
			-0.5f, -0.5f,  0.5f, 0.0f, 0.0f,
			-0.5f,  0.5f,  0.5f, 1.0f, 0.0f,

			 0.5f,  0.5f,  0.5f, 1.0f, 0.0f, //right
			 0.5f,  0.5f, -0.5f, 1.0f, 1.0f,
			 0.5f, -0.5f, -0.5f, 0.0f, 1.0f,

			 0.5f, -0.5f, -0.5f, 0.0f, 1.0f,
			 0.5f, -0.5f,  0.5f, 0.0f, 0.0f,
			 0.5f,  0.5f,  0.5f, 1.0f, 0.0f,

			-0.5f, -0.5f, -0.5f, 0.0f, 1.0f, //back
			 0.5f, -0.5f, -0.5f, 1.0f, 1.0f,
			 0.5f, -0.5f,  0.5f, 1.0f, 0.0f,

			 0.5f, -0.5f,  0.5f, 1.0f, 0.0f,
			-0.5f, -0.5f,  0.5f, 0.0f, 0.0f,
			-0.5f, -0.5f, -0.5f, 0.0f, 1.0f,

			-0.5f,  0.5f, -0.5f, 0.0f, 1.0f, //front
			 0.5f,  0.5f, -0.5f, 1.0f, 1.0f,
			 0.5f,  0.5f,  0.5f, 1.0f, 0.0f,

			 0.5f,  0.5f,  0.5f, 1.0f, 0.0f,
			-0.5f,  0.5f,  0.5f, 0.0f, 0.0f,
			-0.5f,  0.5f, -0.5f, 0.0f, 1.0f
	} };
	int vertexCount = vertices.size()/5;
	unsigned int VBO;
	glCreateBuffers(1, &VBO);
	unsigned int VAO;
	glCreateVertexArrays(1, &VAO);
	glVertexArrayVertexBuffer(VAO, 0, VBO, 0, 5 * sizeof(float));
	glNamedBufferStorage(VBO, vertices.size() * sizeof(float), vertices.data(), GL_DYNAMIC_STORAGE_BIT);
	glEnableVertexArrayAttrib(VAO, 0);
	glEnableVertexArrayAttrib(VAO, 1);
	glVertexArrayAttribFormat(VAO, 0, 3, GL_FLOAT, GL_FALSE, 0);
	glVertexArrayAttribFormat(VAO, 1, 2, GL_FLOAT, GL_FALSE, 3 * sizeof(float));
	glVertexArrayAttribBinding(VAO, 0, 0);
	glVertexArrayAttribBinding(VAO, 1, 0);

	//Make Texture
	glUniform1i(glGetUniformLocation(shader, "basicTexture"), 0);
	int texWidth, texHeight, nrChannels;
	unsigned char* data = stbi_load("textures/wood.jpeg", &texWidth, &texHeight, &nrChannels, STBI_rgb_alpha);
	unsigned int texture;
	glCreateTextures(GL_TEXTURE_2D, 1, &texture);
	glTextureStorage2D(texture, 1, GL_RGBA8, texWidth, texHeight);
	glTextureSubImage2D(texture, 0, 0, 0, texWidth, texHeight, GL_RGBA, GL_UNSIGNED_BYTE, data);
	glTextureParameteri(texture, GL_TEXTURE_WRAP_S, GL_REPEAT);
	glTextureParameteri(texture, GL_TEXTURE_WRAP_T, GL_REPEAT);
	glTextureParameteri(texture, GL_TEXTURE_MIN_FILTER, GL_LINEAR_MIPMAP_LINEAR);
	glTextureParameteri(texture, GL_TEXTURE_MAG_FILTER, GL_LINEAR);
	stbi_image_free(data);

	//set up framebuffer
	glClearColor(0.5f, 0.1f, 0.3f, 1.0f);
	glEnable(GL_DEPTH_TEST);
	glm::mat4 projection_transform = glm::perspective(45.0f, aspectRatio, 0.1f, 10.0f);
	glUniformMatrix4fv(glGetUniformLocation(shader, "projection"), 1, GL_FALSE, glm::value_ptr(projection_transform));

	while (!glfwWindowShouldClose(window)) {

		processInput(window, playerPosition, playerEulers);

		glfwPollEvents();

		//update view
		glm::vec3 forwards{
			glm::sin(glm::radians(playerEulers.y)) * glm::cos(glm::radians(playerEulers.z)),
			glm::sin(glm::radians(playerEulers.y))* glm::sin(glm::radians(playerEulers.z)),
			glm::cos(glm::radians(playerEulers.y))
		};
		glm::vec3 globalUp{ 0.0f, 0.0f, 1.0f };
		glm::vec3 right{ glm::cross(forwards, globalUp) };
		glm::vec3 up{ glm::cross(right,forwards) };
		glm::mat4 view_transform{ glm::lookAt(playerPosition, playerPosition + forwards, up) };
		glUniformMatrix4fv(glGetUniformLocation(shader, "view"), 1, GL_FALSE, glm::value_ptr(view_transform));


		//update transform
		float angle{ glm::radians(static_cast<float>(10 * glfwGetTime())) };
		glm::mat4 model_transform{ glm::mat4(1.0f) };
		model_transform = glm::translate(model_transform, { 1.0f, -3.0f, 0.5f });
		model_transform = glm::rotate(model_transform, angle, { 1.0f, 0.0f, 0.0f });
		model_transform = glm::rotate(model_transform, 2 * angle, { 0.0f, 1.0f, 0.0f });
		glUniformMatrix4fv(glGetUniformLocation(shader, "model"), 1, GL_FALSE, glm::value_ptr(model_transform));

		glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT);
		glUseProgram(shader);
		glBindTextureUnit(0, texture);
		glBindVertexArray(VAO);
		glDrawArrays(GL_TRIANGLES, 0, vertexCount);

		glfwSwapBuffers(window);
		
	}

	//free memory
	glDeleteBuffers(1, &VBO);
	glDeleteVertexArrays(1, &VAO);
	glDeleteProgram(shader);
	glfwTerminate();

	return 0;
}