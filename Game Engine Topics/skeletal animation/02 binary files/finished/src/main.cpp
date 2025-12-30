#include <iostream>
#include <fstream>
#include <sstream>

#include <json/json.h>
#include <glm/glm.hpp>
#include <vector>
/*
	Skeletal Animation.
	Stage 2: Binary files.

	Goals:

		fetch 36 int16s, at an offset of 768, byte length of 72
*/

int main() {

	std::ifstream myBinaryFile;
	std::vector<char> myByteData;

	//Open the file, get its size.
	myBinaryFile.open("src/my_cube.bin", std::ios::binary | std::ios::ate);
	size_t byteCount = myBinaryFile.tellg();
	myByteData.resize(byteCount);
	myBinaryFile.seekg(0);

	//Now read the file
	myBinaryFile.read(myByteData.data(), byteCount);
	myBinaryFile.close();

	//---- Fetch 24 vec3s ----//
	std::cout << "Vec3 Data:" << std::endl;
	size_t vector_count = 24;
	size_t offset = 288;
	size_t byte_size = vector_count * sizeof(glm::vec3);
	std::vector<glm::vec3> fetched_data;
	fetched_data.resize(vector_count);
	memcpy(fetched_data.data(), myByteData.data() + offset, byte_size);

	for (size_t i = 0; i < vector_count; ++i) {
		glm::vec3 v = fetched_data[i];
		std::cout << i << ": <" << v.x << ", " << v.y << ", " << v.z << ">" << std::endl;
	}

	//---- Fetch 72 floats ----//
	std::cout << "Float Data:" << std::endl;
	size_t float_count = 72;
	offset = 288;
	byte_size = float_count * sizeof(float);
	std::vector<float> fetched_data2;
	fetched_data2.resize(float_count);
	memcpy(fetched_data2.data(), myByteData.data() + offset, byte_size);

	for (size_t i = 0; i < float_count; i += 3) {
		float x = fetched_data2[i];
		float y = fetched_data2[i + 1];
		float z = fetched_data2[i + 2];
		std::cout << i << ": <" << x << ", " << y << ", " << z << ">" << std::endl;
	}

	//---- Fetch 36 ints ----//
	std::cout << "Integer Data:" << std::endl;
	size_t int_count = 36;
	offset = 768;
	byte_size = int_count * sizeof(uint16_t);
	std::vector<uint16_t> fetched_data3;
	fetched_data3.resize(int_count);
	memcpy(fetched_data3.data(), myByteData.data() + offset, byte_size);

	for (size_t i = 0; i < int_count; ++i) {
		std::cout << i << ": " << fetched_data3[i] << std::endl;
	}

	return 0;
}