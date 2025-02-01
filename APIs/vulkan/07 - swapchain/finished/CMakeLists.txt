cmake_minimum_required(VERSION 3.28.0)
project(vulkan_fun VERSION 1.0.0)

set(CMAKE_CXX_STANDARD 20)

add_executable(vulkan_fun
    src/backend/glfw_backend.cpp

    src/controller/app.cpp

    src/logging/logger.cpp

    src/renderer/device.cpp
    src/renderer/frame.cpp
    src/renderer/instance.cpp
    src/renderer/renderer.cpp
    src/renderer/swapchain.cpp

    src/main.cpp
)

find_package(Vulkan REQUIRED)

target_include_directories(vulkan_fun 
    PRIVATE
    dependencies 
)

target_link_libraries(vulkan_fun
    glfw
    Vulkan::Vulkan
)