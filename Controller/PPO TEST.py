import time
import os
import random
import torch
import numpy as np
import matplotlib.pyplot as plt
from stable_baselines3 import PPO
from Env import URDFRobotEnv
import pybullet as p

"""
:::::::::::::::::: EVALUATE THE ROBOT AND ITS CONTROLLER :::::::::::::::::: 
"""

# Define simulation parameters
startOrientation = p.getQuaternionFromEuler([0, 0, 0])
startPos = [0, 0, 0.2]
flags = p.URDF_USE_SELF_COLLISION_EXCLUDE_PARENT

dt = 1 / 240.0  # Simulation timestep
# total_simulated_time = 20  # Simulate 20 virtual seconds
# num_steps = int(total_simulated_time / dt)  # Total simulation steps

# Ensure results directory exists
results_dir = "evaluation_results"
os.makedirs(results_dir, exist_ok=True)



# Open the file for writing evaluation results
with open(os.path.join(results_dir, "evaluation_results.txt"), 'w') as f:
    f.write("Evaluation Results:\n\n")

    # Run evaluation for robots
    for i in range(12):
        print("------------- ------------- ------------- ------------- ")
        print(f"------------- Evaluating Robot number {i} -------------")
        print("------------- ------------- ------------- ------------- ")

        ROBOT_URDF_PATH = f"/home/joaoraposo/Documents/GitHub/Evolutionary-Robotics-with-GE/corrected_robot{i}.urdf"
        model_name = f"ppo_robot{i}.zip"

        # Ensure the model file exists
        if not os.path.exists(model_name):
            print(f"Model {model_name} not found. Skipping...")
            continue

        # Load environment and model
        env = URDFRobotEnv(ROBOT_URDF_PATH, startPos, startOrientation, render=True, flags=flags)
        model = PPO.load(model_name)

        # obs, _ = env.reset()
        # env.let_robot_fall()

        # # ------------------------- Test the trained model (visual run)
        # print("\nRunning 20-second real-time test simulation...\n")
        # done = False
        # while not done:
        #     action, _ = model.predict(obs, deterministic=True)
        #     obs, reward, done, truncated, _ = env.step(action)
        #     time.sleep(dt)  # Sync simulation with real-time
        #     robot_pos = env.getRobotPosition()
        #
        """
        ::::::::::::::::: CODE TO FOLLOW THE ROBOT ::::::::::::::::::::::::....
        
        #     # Set camera to follow the robot
        #     p.resetDebugVisualizerCamera(cameraDistance=1,
        #                                  cameraYaw=50,
        #                                  cameraPitch=-30,
        #                                  cameraTargetPosition=robot_pos)
        
        """
        #     print(f"Step Reward: {reward:.2f}")
        #
        #     if done or truncated:
        #         print("Episode ended early during test loop. Resetting...")
        #         obs, _ = env.reset()

        # -------------------------
        # Custom evaluation of the model
        n_eval_episodes = 30
        episode_rewards = []

        print("\nStarting evaluation over multiple episodes...\n")
        for ep in range(n_eval_episodes):
            ep_rewards = []
            obs, _ = env.reset()
            env.let_robot_fall()
            done = False
            while not done:
                action, _ = model.predict(obs, deterministic=False)
                obs, reward, terminated, truncated, _ = env.step(action)

                ep_rewards.append(reward)
                done = terminated or truncated

            episode_total = ep_rewards[-1]
            episode_rewards.append(episode_total)
            print(f"Episode {ep + 1} Final Reward: {ep_rewards[-1]:.2f}")

        mean_reward = np.mean(episode_rewards)
        std_reward = np.std(episode_rewards)

        print(f"\nEvaluation over {n_eval_episodes} episodes: mean_reward = {mean_reward:.2f} +/- {std_reward:.2f}\n")

        # -------------------------
        # Plot the reward history over time
        episodes = np.arange(1, n_eval_episodes + 1)

        plt.figure(figsize=(8, 5))

        # Plot final reward per episode
        plt.plot(episodes, episode_rewards, marker='o', label='Episode Final Reward')

        # Draw a horizontal line for the mean
        plt.axhline(y=mean_reward, color='red', linestyle='--',
                    label=f"Mean Reward = {mean_reward:.2f}")

        # Create a shaded area for ±1 standard deviation around the mean
        plt.fill_between(
            episodes,
            mean_reward - std_reward,
            mean_reward + std_reward,
            color='red',
            alpha=0.2,
            label=f"±1 Std = {std_reward:.2f}"
        )

        plt.xlabel("Episode")
        plt.ylabel("Final Reward")
        plt.title("Episode Final Reward with Mean and Std")
        plt.legend()
        plt.grid(True)
        plt.show()

        # -------------------------
        # Write the results to the file
        f.write(f"Model {i} ({model_name}):\n")
        f.write(f"  Mean Reward = {mean_reward:.2f} +/- {std_reward:.2f}\n\n")

        # Clean up
        obs, _ = env.reset()
        env.close()
