#pragma once
#include "../config.h"

struct SearchResult {
    size_t position;
    int flag;
};

template<typename T>
class ComponentSet {
private:

    SearchResult binary_search(uint32_t entity) {
    
        SearchResult a;
        a.position = 0;
        a.flag = std::min<int>(1, 
            std::max<int>(-1, entities[a.position] - entity));
        if (a.flag == 0) {
            return a;
        }
    
        SearchResult b;
        b.position = entities.size() - 1;
        b.flag = std::min<int>(1, 
            std::max<int>(-1, entities[b.position] - entity));
        if (b.flag == 0) {
            return b;
        }
    
        while ((a.flag * b.flag < 0) 
            && ((b.position - a.position) > 1)) {
        
            SearchResult c;
            c.position = (a.position + b.position) / 2;
            c.flag = std::min<int>(1, 
                std::max<int>(-1, entities[c.position] - entity));
            if (c.flag == 0) {
                return c;
            }
        
            if (a.flag * c.flag < 0) {
                b = c;
            }
            else {
                a = c;
            }
        }
    if (b.flag == 0) {
        return b;
    }
    return a;
}

public:

    std::vector<T> components;
    std::vector<uint32_t> entities;

    void insert(uint32_t entity, T component) {
        //add a new entry, this is sort of a dodgy way
        // to do it though
        entities.push_back(entity);
        components.push_back(component);

        //now shuffle to make room
        size_t i = entities.size() - 1;
        while (i > 0 && entities[i - 1] >= entity) {
            entities[i] = entities[i - 1];
            components[i] = components[i - 1];
            --i;
        }
        entities[i] = entity;
        components[i] = component;
    }

    void remove(uint32_t entity) {
        SearchResult query = binary_search(entity);
        entities.erase(entities.begin() + query.position);
        components.erase(components.begin() + query.position);
    }

    T& get_component(uint32_t entity) {

        SearchResult query = binary_search(entity);
        return components[query.position];
    }
};