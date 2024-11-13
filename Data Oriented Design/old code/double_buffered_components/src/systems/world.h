#pragma once
#include "../components/registry.h"
#include "../config.h"
class World {
public:
	World(ComponentRegistry& componentRegistry);
	void update(float frametime);
private:
	ComponentRegistry& componentRegistry;
};