CPP_COMPILER = g++
C_COMPILER = gcc
SRC_DIRS = src src/control src/view src/model

INCLUDE_FOLDER = -Idependencies
OS_NAME := $(shell uname -s)
C_FLAGS = -O2 -MP -MD
CPP_FLAGS = -std=c++20 -O2 -MP -MD
LIBS =
LIB_FOLDER = -Ldependencies/lib

ifeq ($(OS_NAME), Linux)
	ECHO_MESSAGE = "Linux"
	LIBS += -lGL -lglfw -lrt -lm -ldl
	C_FLAGS += -Wall -Wextra
	CPP_FLAGS += -Wall -Wextra
endif

ifeq ($(OS_NAME), Darwin)
	ECHO_MESSAGE = "macOS"
	LIBS += -framework OpenGL -lglfw
	LIB_FOLDER = -L/usr/local/lib -L/opt/homebrew/lib
	INCLUDE_FOLDER += -I/usr/local/include -I/opt/homebrew/include
endif

FINAL_C_FLAGS = $(INCLUDE_FOLDER) $(C_FLAGS) $(LIB_FOLDER)
FINAL_CPP_FLAGS = $(INCLUDE_FOLDER) $(CPP_FLAGS) $(LIB_FOLDER)

SRC_FILES = $(foreach D, $(SRC_DIRS), $(wildcard $(D)/*.c $(D)/*.cpp))
OBJECTS = $(patsubst %.cpp, %.o, $(patsubst %.c, %.o, $(SRC_FILES)))
DEPENDENCIES = $(patsubst %.o, %.d, $(OBJECTS))

-include $(DEPENDENCIES)

# target: requirements
# $^: inserts the requirements of the rule
# $<: inserts the dependencies of the rule requirements
# $@: inserts the target

%.o: %.c
	$(C_COMPILER) $(FINAL_C_FLAGS) $< -c -o $@

%.o: %.cpp
	$(CPP_COMPILER) $(FINAL_CPP_FLAGS) $< -c -o $@

project: $(OBJECTS)
	$(CPP_COMPILER) $(FINAL_CPP_FLAGS) $(LIBS) $^ -o $@

all: project
	@echo Build complete for $(ECHO_MESSAGE)
	./project

clean:
	rm -rf $(OBJECTS) $(DEPENDENCIES)
