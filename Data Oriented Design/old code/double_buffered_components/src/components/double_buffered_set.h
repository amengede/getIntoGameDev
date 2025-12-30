#pragma once
#include "component_set.h"
#include <array>

template<typename T>
class DoubleBufferedComponentSet {
private:
    std::array<ComponentSet<T>, 2> buffers;
    bool index = 0;

public:

    ComponentSet<T>& get_a_buffer() {
        return buffers[static_cast<int>(!index)];
    }
    
    ComponentSet<T>& get_b_buffer() {
        return buffers[static_cast<int>(index)];
    }

    void flip() {
        index = !index;
    }

    void insert(uint32_t entity, T component) {
        buffers[0].insert(entity, component);
        buffers[1].insert(entity, component);
    }

    void remove(uint32_t entity) {
        buffers[0].remove(entity);
        buffers[1].remove(entity);
    }
};