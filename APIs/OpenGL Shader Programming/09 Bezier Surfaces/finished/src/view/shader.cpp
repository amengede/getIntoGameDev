#include "shader.h"

unsigned int util::load_shader(const shaderFilePathBundle& filepaths) {

	std::vector<unsigned int> modules;

	if (filepaths.vertex) {
		modules.push_back(load_shader_module(filepaths.vertex,GL_VERTEX_SHADER));
	}

	if (filepaths.geometry) {
		modules.push_back(load_shader_module(filepaths.geometry, GL_GEOMETRY_SHADER));
	}

	if (filepaths.tcs) {
		modules.push_back(load_shader_module(filepaths.tcs, GL_TESS_CONTROL_SHADER));
	}

	if (filepaths.tes) {
		modules.push_back(load_shader_module(filepaths.tes, GL_TESS_EVALUATION_SHADER));
	}

	if (filepaths.fragment) {
		modules.push_back(load_shader_module(filepaths.fragment, GL_FRAGMENT_SHADER));
	}

	unsigned int shader = glCreateProgram();
	for (unsigned int shaderModule : modules) {
		glAttachShader(shader, shaderModule);
	}
	glLinkProgram(shader);

	int success;
	char errorLog[1024];
	glGetProgramiv(shader, GL_LINK_STATUS, &success);
	if (!success) {
		glGetProgramInfoLog(shader, 1024, NULL, errorLog);
		std::cout << "Shader linking error:\n" << errorLog << '\n';
	}

	for (unsigned int shaderModule : modules) {
		glDeleteShader(shaderModule);
	}

	return shader;
}

unsigned int util::load_shader_module(const char* filepath, unsigned int type) {

	std::ifstream fileReader;
	std::stringstream bufferedLines;
	std::string line;

	fileReader.open(filepath);
	while (std::getline(fileReader, line)) {
		bufferedLines << line << '\n';
	}
	std::string shaderSource = bufferedLines.str();
	const char* shaderSrc = shaderSource.c_str();
	bufferedLines.str("");
	fileReader.close();

	unsigned int shaderModule = glCreateShader(type);
	glShaderSource(shaderModule, 1, &shaderSrc, NULL);
	glCompileShader(shaderModule);

	int success;
	char errorLog[1024];
	glGetShaderiv(shaderModule, GL_COMPILE_STATUS, &success);
	if (!success) {
		glGetShaderInfoLog(shaderModule, 1024, NULL, errorLog);
		std::cout << "Vertex Shader compilation error:\n" << errorLog << '\n';
	}

	return shaderModule;

}