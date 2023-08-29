#pragma once
#include "../config.h"

class TextureFactory {

public:

    void start_texture_array(int layers);

    void load_into_array(const char* filename, int layer);
    
    unsigned int finalize_texture_array();

private:

    unsigned int rows, cols;

    unsigned int texture;

};