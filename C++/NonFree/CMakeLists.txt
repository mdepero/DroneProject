cmake_minimum_required(VERSION 2.8)
project( NonFree )
find_package( OpenCV REQUIRED )
add_executable( NonFree NonFree.cpp)
target_link_libraries( NonFree ${OpenCV_LIBS} )
set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -std=c++11")
