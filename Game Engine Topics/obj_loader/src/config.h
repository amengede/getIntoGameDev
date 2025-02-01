#pragma once
#include <glm/glm.hpp>
#include <unordered_map>
#include <string>

std::vector<std::string> split(std::string line, std::string delimiter);
int random_int_in_range(int range);
float random_float();

enum class ObjectType {
    eAlice,
    eCreepyGirl,
    eDodemon,
    eGhost,
    eHandMonster,
    eMieruko,
    eMonsterPlant,
};

static std::vector<const char*> objNames = {
    "models/alice.obj",         //Alice
    "models/creepy_girl.obj",   //Creepy Girl
    "models/dodemon.obj",       //Dodemon
    "models/ghost.obj",         //Ghost
    "models/hand_monster.obj",  //Hand Monster
    "models/mieruko.obj",       //Mieruko
    "models/monster_plant.obj", //Monster Plant
};

static std::vector<const char*> mtlNames = {
    "models/alice.mtl",         //Alice
    "models/creepy_girl.mtl",   //Creepy Girl
    "models/dodemon.mtl",       //Dodemon
    "models/ghost.mtl",         //Ghost
    "models/hand_monster.mtl",  //Hand Monster
    "models/mieruko.mtl",       //Mieruko
    "models/monster_plant.mtl", //Monster Plant
};

static std::vector<float> scales = {
    0.01f,  //Alice
    1.0f,   //Creepy Girl
    1.0f,   //Dodemon
    0.5f,   //Ghost
    2.0f,   //Hand Monster
    0.1f,   //Mieruko
    0.01f,  //Monster Plant
};

struct Mesh {
    uint32_t elementCount, VAO, VBO, EBO, material;
};

constexpr float windowWidth = 1920.0f;
constexpr float windowHeight = 1080.0f;

constexpr uint32_t maxObjectCount = 1000;
constexpr uint32_t objectTypeCount = 7;