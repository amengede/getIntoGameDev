#pragma once
#include "../config.h"

class FrameBuffer {
public:
	void build(unsigned int width, unsigned int height);
	~FrameBuffer();
	void draw_to();
	void read_from();
private:
	unsigned int frameBuffer, colorAttachment, depthAttachment;
};