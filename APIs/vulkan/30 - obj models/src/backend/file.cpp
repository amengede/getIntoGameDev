#include "file.h"
#include <fstream>
#include <sstream>
#include "../logging/logger.h"

DynamicArray<char> read_file(const char* filename) {

    Logger* logger = Logger::get_logger();
	
    // Open file at the end, log error if file can't be opened
    std::ifstream file(filename, std::ios::ate | std::ios::binary);
    if (!file.is_open()) {
        std::stringstream line_builder;
        line_builder << "Failed to load \"" 
            << filename << "\"" << std::endl;
        std::string line = line_builder.str();
        logger->print(line);
    }

    // End position indicates file size
    size_t filesize{ static_cast<size_t>(file.tellg()) };

    // Rewind and read contents
    DynamicArray<char> buffer;
    buffer.resize(filesize);
    file.seekg(0);
    file.read(buffer.data, filesize);

    file.close();
    return buffer;
}

DynamicArray<std::string> split(std::string line, std::string delimiter) {

    DynamicArray<std::string> splitLine;

    size_t pos = 0;
    std::string token;
    while ((pos = line.find(delimiter)) != std::string::npos) {
        token = line.substr(0, pos);
        splitLine.push_back(token);
        line.erase(0, pos + delimiter.length());
    }
    splitLine.push_back(line);

    return splitLine;
}