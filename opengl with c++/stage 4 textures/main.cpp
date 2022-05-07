#include <glad/glad.h>
#include <GLFW/glfw3.h>
#include <iostream>
#include <vector>
#define STB_IMAGE_IMPLEMENTATION
#include "stb_image.h"

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

void processInput(GLFWwindow* window) {
	if (glfwGetKey(window, GLFW_KEY_ESCAPE) == GLFW_PRESS) {
		glfwSetWindowShouldClose(window, true);
	}
}

unsigned int makeProgram() {
	const char* vertexShaderSource = "#version 450 core\n"
		"layout (location = 0) in vec3 vertexPosition;\n"
		"layout (location = 1) in vec3 vertexColor;\n"
		"layout (location = 2) in vec2 vertexTexCoords;\n"
		"layout (location = 0) out vec3 fragmentColor;\n"
		"layout (location = 1) out vec2 fragmentTexCoords;\n"
		"void main()\n"
		"{\n"
		"    gl_Position = vec4(vertexPosition, 1.0);\n"
		"    fragmentColor = vertexColor;\n"
		"    fragmentTexCoords = vec2(vertexTexCoords.x, 1.0 - vertexTexCoords.y);\n"
		"}\0";

	const char* fragmentShaderSource = "#version 450 core\n"
		"layout (location = 0) in vec3 fragmentColor;\n"
		"layout (location = 1) in vec2 fragmentTexCoords;\n"
		"uniform sampler2D basicTexture;\n"
		"out vec4 finalColor;\n"
		"void main()\n"
		"{\n"
		"    finalColor = vec4(fragmentColor, 1.0) * texture(basicTexture, fragmentTexCoords);\n"
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

	int width = 640;
	int height = 480;
	GLFWwindow* window = initialize(width, height);
	if (!window) {
		glfwTerminate();
		return -1;
	}

	unsigned int shader = makeProgram(); 
	glUseProgram(shader);

	//texture coordinates: s:horizontal, t:vertical
	//x,y,z,r,g,b,s,t
	std::vector<float> vertices = { {
			-0.25f, -0.25f, 0.0f, 1.0f, 0.0f, 0.0f, 0.0f, 0.0f,
			 0.25f, -0.25f, 0.0f, 0.0f, 1.0f, 0.0f, 1.0f, 0.0f,
			 0.0f,  0.25f, 0.0f, 0.0f, 0.0f, 1.0f, 0.5f, 1.0f
	} };

	int vertexCount = 3;

	unsigned int VBO;
	glCreateBuffers(1, &VBO);

	unsigned int VAO;
	glCreateVertexArrays(1, &VAO);
	glVertexArrayVertexBuffer(VAO, 0, VBO, 0, 8 * sizeof(float));

	glNamedBufferStorage(VBO, vertices.size() * sizeof(float), vertices.data(), GL_DYNAMIC_STORAGE_BIT);

	glEnableVertexArrayAttrib(VAO, 0);
	glEnableVertexArrayAttrib(VAO, 1);
	glEnableVertexArrayAttrib(VAO, 2);
	glVertexArrayAttribFormat(VAO, 0, 3, GL_FLOAT, GL_FALSE, 0);
	glVertexArrayAttribFormat(VAO, 1, 3, GL_FLOAT, GL_FALSE, 3 * sizeof(float));
	glVertexArrayAttribFormat(VAO, 2, 2, GL_FLOAT, GL_FALSE, 6 * sizeof(float));
	glVertexArrayAttribBinding(VAO, 0, 0);
	glVertexArrayAttribBinding(VAO, 1, 0);
	glVertexArrayAttribBinding(VAO, 2, 0);

	//Texture
	//set the texture to texture unit 0 within the shader
	glUniform1i(glGetUniformLocation(shader, "basicTexture"), 0);

	//load the image
	int texWidth, texHeight, nrChannels;
	unsigned char* data = stbi_load("textures/wood.jpeg", &texWidth, &texHeight, &nrChannels, STBI_rgb_alpha);

	//make the texture
	unsigned int texture;
	glCreateTextures(GL_TEXTURE_2D, 1, &texture);
	//declare storage
	//(texture, levels, internal format, width, height)
	glTextureStorage2D(texture, 1, GL_RGBA8, texWidth, texHeight);
	//pass in data
	//(texture, level, xoffset, yoffset, width, height, image format, data type, data pointer)
	glTextureSubImage2D(texture, 0, 0, 0, texWidth, texHeight, GL_RGBA, GL_UNSIGNED_BYTE, data);

	//texture parameters
	glTextureParameteri(texture, GL_TEXTURE_WRAP_S, GL_REPEAT);
	glTextureParameteri(texture, GL_TEXTURE_WRAP_T, GL_REPEAT);
	glTextureParameteri(texture, GL_TEXTURE_MIN_FILTER, GL_LINEAR_MIPMAP_LINEAR);
	glTextureParameteri(texture, GL_TEXTURE_MAG_FILTER, GL_LINEAR);

	stbi_image_free(data);

	while (!glfwWindowShouldClose(window)) {

		processInput(window);

		glfwPollEvents();

		glClearColor(0.5f, 0.1f, 0.3f, 1.0f);
		glClear(GL_COLOR_BUFFER_BIT);
		glUseProgram(shader);

		//bind the texture
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