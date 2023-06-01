#include "config.h"

std::vector<std::string> split(std::string line, std::string delimiter) {

	std::vector<std::string> split_line;

	size_t pos = 0;
	std::string token;
	while ((pos = line.find(delimiter)) != std::string::npos) {
		token = line.substr(0, pos);
		split_line.push_back(token);
		line.erase(0, pos + delimiter.length());
	}
	split_line.push_back(line);

	return split_line;
}

inline float random_float() {
	static std::uniform_real_distribution<float> distribution(0.0f, 1.0f);
	static std::mt19937 generator;
	return distribution(generator);
}

inline float random_float(float min, float max) {
	return min + random_float() * (max - min);
}