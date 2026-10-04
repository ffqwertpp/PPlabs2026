cmake_minimum_required(VERSION 3.10)
project(matmul CXX)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

# По умолчанию собираем с оптимизацией: без неё замеры времени бессмысленны
if(NOT CMAKE_BUILD_TYPE AND NOT CMAKE_CONFIGURATION_TYPES)
  set(CMAKE_BUILD_TYPE Release)
endif()

add_executable(matmul src/matmul.cpp)

if(MSVC)
  target_compile_options(matmul PRIVATE /W3)
else()
  target_compile_options(matmul PRIVATE -Wall -Wextra)
endif()
