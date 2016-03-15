cmake_minimum_required(VERSION 2.8)
project(cubes)

find_package(OpenGL REQUIRED)

add_subdirectory(glfw)

include_directories(${OPENGL_INCLUDE_DIR})
include_directories(glfw/include)

set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -I/usr/local/include -O2 -Wall -Wextra -std=c++11")

set(SOURCE_FILES main.cpp)
add_executable(cubes ${SOURCE_FILES})

target_link_libraries(cubes glfw ${GLFW_LIBRARIES} ${OPENGL_LIBRARY})
