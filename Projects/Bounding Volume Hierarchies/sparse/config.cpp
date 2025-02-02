#include "config.h"

inline float random_float() {
    static std::uniform_real_distribution<float> distribution(0.0f, 1.0f);
    static std::mt19937 generator;
    return distribution(generator);
}

inline float random_float(float min, float max) {
    return min + random_float() * (max - min);
}

inline glm::vec3 random_vec() {
    return glm::vec3(random_float(), random_float(), random_float());
}

inline glm::vec3 random_vec(float min, float max) {
    return glm::vec3(random_float(min, max), random_float(min, max), random_float(min, max));
}

glm::vec3 random_in_unit_sphere() {

    float theta{ random_float(0, 2.0f * glm::pi<float>()) };
    float phi{ random_float(0, glm::pi<float>()) };

    return glm::vec3(glm::cos(theta) * glm::sin(phi), glm::sin(theta) * glm::sin(phi), glm::cos(phi));
}