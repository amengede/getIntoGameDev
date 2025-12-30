/*---------------------------------------------------------------------------*/
/*	Utility functions for dealing with files
/*---------------------------------------------------------------------------*/
#pragma once
#include "dynamic_array.h"
#include <string>

/**
 * @brief Read a file
 * 
 * @param filename file to open
 * @return std::vector<char> contents of file
 */
DynamicArray<char> read_file(const char* filename);

/**
* @brief split a line
* 
* @param line the string to split
* @param delimiter the token to split on
* 
* @returns the set of substrings
*/
DynamicArray<std::string> split(std::string line, std::string delimiter);
/*---------------------------------------------------------------------------*/