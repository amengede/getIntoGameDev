/*---------------------------------------------------------------------------*/
/*	Custom Vector
/*---------------------------------------------------------------------------*/
#pragma once
template<typename T>
class DynamicArray {
public:
	size_t	size, capacity;
	T* data;

	// Default constructor
	DynamicArray() {
		size = 0;
		capacity = 0;
		data = nullptr;
	}

	// Copy constructor
	DynamicArray(const DynamicArray& other) {
		size = other.size;
		capacity = other.capacity;
		data = new T[other.capacity];
		for (int index = 0; index < other.size; ++index) {
			data[index] = other.data[index];
		}
	}

	// Copy Assignment
	DynamicArray<T>& operator=(const DynamicArray<T>& rhs) {

		if (this == &rhs) {
			return *this;
		}

		if (rhs.size <= capacity) {
			size = rhs.size;
			for (int index = 0; index < rhs.size; ++index) {
				data[index] = rhs.data[index];
			}
			return *this;
		}

		T* newData = new T[rhs.size];

		for (int index = 0; index < rhs.size; ++index) {
			newData[index] = rhs.data[index];
		}

		delete[] data;
		size = rhs.size;
		capacity = rhs.size;
		data = newData;
		return *this;
	}

	~DynamicArray() {
		delete[] data;
	}

	void reserve(size_t newCapacity) {

		if (newCapacity <= capacity) {
			return;
		}

		T* newData = new T[newCapacity];

		for (int i = 0; i < size; ++i) {
			newData[i] = data[i];
		}

		delete[] data;

		data = newData;

		capacity = newCapacity;
	}

	void resize(size_t newSize, T val = T()) {

		reserve(newSize);

		for (size_t index = size; index < newSize; ++index) {
			data[index] = val;
		}

		size = newSize;
	}

	void clear() {
		size = 0;
	}

	void push_back(const T& element) {

		if (capacity == 0) {
			reserve(8);
		}
		else if (size == capacity) {
			reserve(2 * capacity);
		}

		data[size++] = element;
	}

	T& operator[](size_t i) {
		return data[i];
	}

	const T& operator[](size_t i) const {
		return data[i];
	}
};
/*---------------------------------------------------------------------------*/