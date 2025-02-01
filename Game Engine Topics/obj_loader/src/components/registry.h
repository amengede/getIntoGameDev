#pragma once
#include "../config.h"
#include "components.h"
#include "component_set.h"

/*
    Basically holds all components in the game.
*/
struct ComponentRegistry {
    ComponentSet<TransformComponent> transforms;
    ComponentSet<VelocityComponent> velocities;
    ComponentSet<RenderComponent> renderables;
};