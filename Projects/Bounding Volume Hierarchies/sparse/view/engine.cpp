#include "engine.h"
#include "../model/node.h"

Engine::Engine(int width, int height) {

	shader = util::load_shader("shaders/vertex.txt", "shaders/fragment.txt");
	glUseProgram(shader);

	glClearColor(0.0f, 0.0f, 0.0f, 1.0f);

	this->width = width;
	this->height = height;
	screenMesh = new QuadModel;
	
	targetFramerate = 30;
	framerateMargin = 5;
	sampleCount = 4;
	bounceCount = 4;

	create_LOD_chain();
	create_color_buffers();

}

Engine::~Engine() {
	delete screenMesh;
	glDeleteTextures(colorBuffers.size(), colorBuffers.data());
	glDeleteProgram(shader);
}

void Engine::create_LOD_chain() {

	unsigned int tempWidth = width;
	unsigned int tempHeight = height;
	resolutions.push_back({ tempWidth, tempHeight });
	

	while (tempWidth > 2 && tempHeight > 2) {
		tempWidth = static_cast<unsigned int>(tempWidth / 1.25);
		tempHeight = static_cast<unsigned int>(tempHeight / 1.25);
		resolutions.push_back({ tempWidth, tempHeight });
	}

	resolutionLevel = static_cast<unsigned int>(resolutions.size()) - 1;
	//resolutionLevel = 0;
	width = resolutions[resolutionLevel].width;
	height = resolutions[resolutionLevel].height;

}

void Engine::create_color_buffers() {

	for (FrameSize frame : resolutions) {

		unsigned int tempWidth = frame.width;
		unsigned int tempHeight = frame.height;

		unsigned int newColorBuffer = 0;
		glGenTextures(1, &newColorBuffer);
		glActiveTexture(GL_TEXTURE0);
		glBindTexture(GL_TEXTURE_2D, newColorBuffer);

		glTextureParameteri(newColorBuffer, GL_TEXTURE_WRAP_S, GL_REPEAT);
		glTextureParameteri(newColorBuffer, GL_TEXTURE_WRAP_T, GL_REPEAT);
		glTextureParameteri(newColorBuffer, GL_TEXTURE_MIN_FILTER, GL_NEAREST);
		glTextureParameteri(newColorBuffer, GL_TEXTURE_MAG_FILTER, GL_LINEAR);
		glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA8, width, height, 0, GL_RGBA, GL_UNSIGNED_BYTE, NULL);
		
		colorBuffers.push_back(newColorBuffer);

		std::vector <uint32_t> newColorBufferMemory;
		for (int y = 0; y < tempHeight; ++y) {
			for (int x = 0; x < tempWidth; ++x) {
				newColorBufferMemory.push_back(0);
			}
		}
		colorBufferMemories.push_back(newColorBufferMemory);
	}

	colorBuffer = colorBuffers[resolutionLevel];
	colorBufferMemory = colorBufferMemories[resolutionLevel];

}

void Engine::pset(size_t x, size_t y, glm::vec3 color) {

	uint8_t r = std::max(0,std::min(255,(int)(255 * glm::sqrt(color.x))));
	uint8_t g = std::max(0, std::min(255,(int)(255 * glm::sqrt(color.y))));
	uint8_t b = std::max(0, std::min(255,(int)(255 * glm::sqrt(color.z))));
	colorBufferMemory[x + (size_t)width * y] = r + (g << 8) + (b << 16) + (255 << 24);

}

glm::vec3 Engine::ray_color(Ray& ray, Scene* scene, int depth) {

	hit_record rec;

	if (depth <= 0) {
		return glm::vec3(0.0f);
	}

	bool hit_something = false;
	float t_min = 0.00001f;
	float t_max = 9999;

	//Traverse scene's BVH
	std::queue<Node*> nodes;
	nodes.push(scene->root);
	while (!nodes.empty()) {
		Node* node = nodes.front();
		nodes.pop();

		if (!node) {
			continue;
		}

		if (node->volume->hit(ray)) {

			if (node->isInternal) {
				for (Node* child : node->children) {
					if (child) {
						nodes.push(child);
					}
				}
			}
			else {
				for (Sphere* sphere : node->spheres) {
					if (sphere->hit(ray, t_min, t_max, rec)) {
						hit_something = true;
						t_max = rec.t;
					}
				}

			}
		}

	}

	if (hit_something) {
		Ray newRay(rec.point, glm::normalize(rec.normal + 0.9f * random_in_unit_sphere()));
		return 0.5f * rec.color * ray_color(newRay, scene, depth - 1);
	}

	glm::vec3 unit_direction{ glm::normalize(ray.direction) };
	float t = 0.5f * (unit_direction.z + 1.0f);
	return (1.0f - t) * glm::vec3(1.0f, 1.0f, 1.0f) + t * glm::vec3(0.5f, 0.7f, 1.0f);
}

void Engine::render(Scene* scene) {

	//auto start = std::chrono::high_resolution_clock::now();

	for (int y = 0; y < height; ++y) {
		//std::cout << y << " / " << height << std::endl;
		for (int x = 0; x < width; ++x) {
			glm::vec3 color = glm::vec3(0.0f);
			for (int sample = 0; sample < sampleCount; ++sample) {
				//float horizontalCoefficient = ((float(x) * 2 - width) / width);
				//float verticalCoefficient = ((float(y) * 2 - height) / width);
				float horizontalCoefficient = 2.0f * (x + random_float()) / (width)-1.0f;
				float verticalCoefficient = 2.0f * (y + random_float()) / (width)-1.0f;
				Ray ray(scene->player->position, glm::normalize(scene->player->forwards + horizontalCoefficient * scene->player->right + verticalCoefficient * scene->player->up));
				color = color + (1.0f / sampleCount) * ray_color(ray, scene, bounceCount);
			}
			pset(x, y, color);
		}
	}

	//auto stop = std::chrono::high_resolution_clock::now();
	//auto duration = std::chrono::duration_cast<std::chrono::milliseconds>(stop - start);
	//std::cout << "This render took " << duration.count() << " ms." << std::endl;
}

void Engine::draw_screen() {

	glUseProgram(shader);

	glActiveTexture(GL_TEXTURE0);
	glBindTexture(GL_TEXTURE_2D, colorBuffer);

	glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA8, width, height, 0, GL_RGBA, GL_UNSIGNED_BYTE, colorBufferMemory.data());

	glBindVertexArray(screenMesh->VAO);
	glDrawArrays(GL_TRIANGLES, 0, 6);
	glFlush();

}

void Engine::adapt_framerate(int framerate) {

	if (framerate > targetFramerate + framerateMargin && resolutionLevel > 0) {
		resolutionLevel -= 1;
	}
	else if (framerate < targetFramerate - framerateMargin && resolutionLevel < resolutions.size() - 1) {
		resolutionLevel += 1;
	}

	width = resolutions[resolutionLevel].width;
	height = resolutions[resolutionLevel].height;

	colorBuffer = colorBuffers[resolutionLevel];
	colorBufferMemory = colorBufferMemories[resolutionLevel];
}