#include <glad/glad.h>
#include <GLFW/glfw3.h>
#include <iostream>
#include <vector>

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

int main() {

	int width = 640;
	int height = 480;
	GLFWwindow* window = initialize(width, height);
	if (!window) {
		glfwTerminate();
		return -1;
	}

	unsigned int shader = makeProgram(); 
	//nine out of ten unexpected errors in OpenGL are caused by not using the right program.
	glUseProgram(shader);


	//triangle data, using vector type to store a list of floats
	// x,y,z,r,g,b
	std::vector<float> vertices = { {
			-0.25f, -0.25f, 0.0f, 1.0f, 0.0f, 0.0f,
			 0.25f, -0.25f, 0.0f, 0.0f, 1.0f, 0.0f,
			 0.0f,  0.25f, 0.0f, 0.0f, 0.0f, 1.0f
	} };

	int vertexCount = 3;

	//this data exists on the cpu side, we need to get it to the gpu side.
	//This is done with a vertex buffer object (vbo)
	unsigned int VBO;
	glCreateBuffers(1, &VBO);

	//a vertex array object stores data and attribute information
	unsigned int VAO;
	glCreateVertexArrays(1, &VAO);
	//bind the vertex buffer object to the VAO
	//(VAO, binding index, VBO, offset, stride)
	glVertexArrayVertexBuffer(VAO, 0, VBO, 0, 6 * sizeof(float));

	//send data to our new VBO. memory is allocated at this point (VBO will have to be deleted later)
	//(VBO, size in bytes, pointer to data start, mode)
	glNamedBufferStorage(VBO, vertices.size() * sizeof(float), vertices.data(), GL_DYNAMIC_STORAGE_BIT);
	/*
		DYNAMIC_STORAGE: data may be updated after creation through glBufferSubData()
		MAP_READ: data can be read
		MAP_WRITE: data can be written to
		MAP_PERSISTENT: data can be worked with by the GPU while mapped (taking CPU instructions like read/write)
		MAP_COHERENT: read/write instructions are executed immediately
		CLIENT_STORAGE: store buffer data on client (CPU) side
	*/

	/*
		the data has been loaded into the GPU's vram (video ram),
		however the GPU doesn't know how to use it.
		Where is the position data, where is the color data?
		We need to create attribute pointers to describe how to get the attributes out
		of that list of big, dumb numbers.
	*/
	glEnableVertexArrayAttrib(VAO, 0);
	glEnableVertexArrayAttrib(VAO, 1);
	//(VAO, location, size, type, should be normalized, (void*)offset)
	glVertexArrayAttribFormat(VAO, 0, 3, GL_FLOAT, GL_FALSE, 0);
	glVertexArrayAttribFormat(VAO, 1, 3, GL_FLOAT, GL_FALSE, 3 * sizeof(float));
	//(VAO, location, binding)
	glVertexArrayAttribBinding(VAO, 0, 0);
	glVertexArrayAttribBinding(VAO, 1, 0);

	//game loop
	while (!glfwWindowShouldClose(window)) {

		processInput(window);

		glfwPollEvents();

		//draw triangle
		glClearColor(0.5f, 0.1f, 0.3f, 1.0f);
		glClear(GL_COLOR_BUFFER_BIT);
		glUseProgram(shader);
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