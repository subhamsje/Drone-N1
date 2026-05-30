cmake_minimum_required(VERSION 3.8)
project(altaria_gazebo_bridge)

if(CMAKE_COMPILER_IS_GNUCXX OR CMAKE_CXX_COMPILER_ID MATCHES "Clang")
  add_compile_options(-Wall -Wextra -Wpedantic)
endif()

find_package(ament_cmake REQUIRED)
find_package(rclcpp REQUIRED)
find_package(rclcpp_action REQUIRED)
find_package(rosidl_default_generators REQUIRED)

rosidl_generate_interfaces(${PROJECT_NAME}
  "action/SpawnBranch.action"
)

add_executable(gazebo_branch_server src/gazebo_branch_server.cpp)
ament_target_dependencies(gazebo_branch_server rclcpp rclcpp_action)
rosidl_target_interfaces(gazebo_branch_server ${PROJECT_NAME} "rosidl_typesupport_cpp")

install(TARGETS
  gazebo_branch_server
  DESTINATION lib/${PROJECT_NAME}
)

ament_package()
