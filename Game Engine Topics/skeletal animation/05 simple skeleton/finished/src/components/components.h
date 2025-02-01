#pragma once
#include "../config.h"

struct BoneComponent {
    glm::vec3 position;
    glm::quat rotation;
    glm::mat4 transform;
    std::vector<unsigned int> children;
};

struct Skeleton {
    std::vector<BoneComponent> bones;
};

struct RenderComponent {
    ObjectType objectType;
};

struct TransformComponent {
    glm::vec3 position;
    glm::vec3 eulers;
};

struct KeyframeSpan {
    unsigned int length, next, target;
    glm::quat rotation_a, rotation_b;
};

struct Animations {
    std::vector<KeyframeSpan> spans;
};

struct Playhead {
    unsigned int t, span;
};

struct Animation {
    std::vector<Playhead> playheads;
};