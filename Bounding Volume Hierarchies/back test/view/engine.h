#pragma once
#include "../config.h"
#include "../model/scene.h"
#include "shader.h"
#include "quad_model.h"
#include "../model/hit_record.h"
#include "../model/ray.h"

struct FrameSize {
	unsigned int width, height;
};

class Engine {
public:
	Engine(int width, int height);
	~Engine();

	void render(Scene* scene);
	void create_LOD_chain();
	void create_color_buffers();
	void draw_screen();
	void adapt_framerate(int framerate);
	void pset(size_t x, size_t y, glm::vec3 color);
	glm::vec3 ray_color(Ray& r, Scene* scene, int depth);
	int sampleCount, bounceCount;

	unsigned int shader, width, height, targetFramerate, framerateMargin;
	unsigned int colorBuffer, resolutionLevel;
	std::vector<uint32_t> colorBufferMemory;
	std::vector<unsigned int> colorBuffers;
	std::vector<FrameSize> resolutions;
	QuadModel* screenMesh;
	std::vector<std::vector<uint32_t>> colorBufferMemories;
};