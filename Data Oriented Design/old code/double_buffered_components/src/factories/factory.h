#pragma once
#include "../config.h"
#include "../components/registry.h"

class Factory {

public:
    Factory(ComponentRegistry& componentRegistry, uint32_t& shader);

    void make_mesh();

    std::vector<unsigned int> garbage_bin;

private:

    unsigned int entities_made = 0;

    ComponentRegistry& componentRegistry;
    uint32_t& shader;

    unsigned int allocate_id();

};