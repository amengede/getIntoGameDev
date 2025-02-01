#include "file.h"
#include <fstream>
#include <sstream>
#include "../logging/logger.h"

std::vector<char> read_file(const char* filename) {

    Logger* logger = Logger::get_logger();
		
    std::ifstream file(filename, std::ios::ate | std::ios::binary);

    if (!file.is_open()) {
        std::stringstream line_builder;
        line_builder << "Failed to load \"" 
            << filename << "\"" << std::endl;
        std::string line = line_builder.str();
        logger->print(line);
    }

    size_t filesize{ static_cast<size_t>(file.tellg()) };

    std::vector<char> buffer(filesize);
    file.seekg(0);
    file.read(buffer.data(), filesize);

    file.close();
    return buffer;
}