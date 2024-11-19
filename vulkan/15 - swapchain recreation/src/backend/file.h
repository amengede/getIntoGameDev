#pragma once
#include <vector>

/**
 * @brief Read a file
 * 
 * @param filename file to open
 * @return std::vector<char> contents of file
 */
std::vector<char> read_file(const char* filename);