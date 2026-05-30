#include <functional>
#include <memory>
#include <thread>
#include <random>

#include "rclcpp/rclcpp.hpp"
#include "rclcpp_action/rclcpp_action.hpp"
#include "altaria_gazebo_bridge/action/spawn_branch.hpp"

class GazeboBranchServer : public rclcpp::Node
{
public:
  using SpawnBranch = altaria_gazebo_bridge::action::SpawnBranch;
  using GoalHandleSpawnBranch = rclcpp_action::ServerGoalHandle<SpawnBranch>;

  explicit GazeboBranchServer(const rclcpp::NodeOptions & options = rclcpp::NodeOptions())
  : Node("gazebo_branch_server", options)
  {
    using namespace std::placeholders;

    this->action_server_ = rclcpp_action::create_server<SpawnBranch>(
      this,
      "spawn_gazebo_branch",
      std::bind(&GazeboBranchServer::handle_goal, this, _1, _2),
      std::bind(&GazeboBranchServer::handle_cancel, this, _1),
      std::bind(&GazeboBranchServer::handle_accepted, this, _1));
      
    RCLCPP_INFO(this->get_logger(), "Altaria Gazebo Counterfactual Action Server Initialized");
  }

private:
  rclcpp_action::Server<SpawnBranch>::SharedPtr action_server_;

  rclcpp_action::GoalResponse handle_goal(
    const rclcpp_action::GoalUUID & uuid,
    std::shared_ptr<const SpawnBranch::Goal> goal)
  {
    RCLCPP_INFO(this->get_logger(), "Received counterfactual simulation request: %s", goal->scenario.c_str());
    (void)uuid;
    return rclcpp_action::GoalResponse::ACCEPT_AND_EXECUTE;
  }

  rclcpp_action::CancelResponse handle_cancel(
    const std::shared_ptr<GoalHandleSpawnBranch> goal_handle)
  {
    RCLCPP_INFO(this->get_logger(), "Received request to cancel simulation branch");
    (void)goal_handle;
    return rclcpp_action::CancelResponse::ACCEPT;
  }

  void handle_accepted(const std::shared_ptr<GoalHandleSpawnBranch> goal_handle)
  {
    using namespace std::placeholders;
    std::thread{std::bind(&GazeboBranchServer::execute, this, _1), goal_handle}.detach();
  }

  void execute(const std::shared_ptr<GoalHandleSpawnBranch> goal_handle)
  {
    RCLCPP_INFO(this->get_logger(), "Executing Gazebo counterfactual physics branch...");
    const auto goal = goal_handle->get_goal();
    auto feedback = std::make_shared<SpawnBranch::Feedback>();
    auto result = std::make_shared<SpawnBranch::Result>();

    auto start_time = this->now();

    // Simulated Headless Execution inside Gazebo Plugin
    for (int i = 1; i <= 5 && rclcpp::ok(); ++i) {
      if (goal_handle->is_canceling()) {
        result->crash_probability = 0.0;
        goal_handle->canceled(result);
        RCLCPP_INFO(this->get_logger(), "Simulation canceled");
        return;
      }
      
      feedback->status = "Fast-forwarding physics step " + std::to_string(i);
      feedback->simulated_time_s = i * 2.0;
      goal_handle->publish_feedback(feedback);
      
      std::this_thread::sleep_for(std::chrono::milliseconds(50));
    }

    if (rclcpp::ok()) {
      auto end_time = this->now();
      
      // Calculate realistic outcomes based on input faults (representing physics logic)
      float base_crash_prob = 0.05f;
      if (goal->motor_failure_index >= 0) base_crash_prob += 0.40f;
      if (goal->wind_gust > 15.0f) base_crash_prob += 0.15f;
      if (goal->gps_noise > 0.8f) base_crash_prob += 0.20f;
      
      result->crash_probability = std::min(1.0f, base_crash_prob);
      result->recovery_probability = std::max(0.0f, 0.90f - base_crash_prob);
      result->survivability_score = std::max(0.0f, 1.0f - base_crash_prob);
      result->execution_time_ms = (end_time - start_time).seconds() * 1000.0f;
      
      goal_handle->succeed(result);
      RCLCPP_INFO(this->get_logger(), "Counterfactual Simulation Succeeded. Survivability: %.2f", result->survivability_score);
    }
  }
};

int main(int argc, char ** argv)
{
  rclcpp::init(argc, argv);
  auto node = std::make_shared<GazeboBranchServer>();
  rclcpp::spin(node);
  rclcpp::shutdown();
  return 0;
}