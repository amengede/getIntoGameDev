#include "config.h"

float random_float() {
    static std::uniform_real_distribution<float> distribution(0.0f, 1.0f);
    static std::mt19937 generator;
    return distribution(generator);
}

float random_float(float min, float max) {
    return min + random_float() * (max - min);
}

glm::vec3 random_vec() {
    return glm::vec3(random_float(), random_float(), random_float());
}

glm::vec3 random_vec(float min, float max) {
    return glm::vec3(random_float(min, max), random_float(min, max), random_float(min, max));
}