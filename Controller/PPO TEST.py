import time
import os
import random
import torch
import numpy as np
import matplotlib.pyplot as plt
from stable_baselines3 import PPO
from Env import URDFRobotEnv
import pybullet as p

# TODO CORRIGIR O PATH DEPOIS DO CONTROLADOR E O FOR CYCLE TBM

"""
:::::::::::::::::: EVALUATE THE ROBOT AND ITS CONTROLLER :::::::::::::::::: 
"""
walker = os.walk("models_PPO_Test")

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
    for i in range(1):
        print("------------- ------------- ------------- ------------- ")
        print(f"------------- Evaluating Robot number {i} -------------")
        print("------------- ------------- ------------- ------------- ")

        ROBOT_URDF_PATH = f"/home/joaoraposo/Documents/GitHub/Evolutionary-Robotics-with-GE/corrected_robot{0}.urdf"
        #model_name = f"ppo_robot{0}.zip"
        model_name = f"testVandF_robot{0}.zip"

        model = PPO.load(model_name)

        # # Ensure the model file exists
        # if not os.path.exists(model_name):
        #     print(f"Model {model_name} not found. Skipping...")
        #     continue

        # Load environment and model
        env = URDFRobotEnv(ROBOT_URDF_PATH, startPos, startOrientation, render=True, flags=flags)

        # # ------------------------- Test the trained model (visual run)
        # print("\nRunning 20-second real-time test simulation...\n")
        # done = False
        # while not done:
        #     action, _ = model.predict(obs, deterministic=True)
        #     obs, reward, done, truncated, _ = env.step(action)
        #     time.sleep(dt)  # Sync simulation with real-time
        #     robot_pos = env.getRobotPosition()

        robot_pos = env.getRobotPosition()
        # Set camera to follow the robot
        p.resetDebugVisualizerCamera(cameraDistance=1,
                                              cameraYaw=50,
                                              cameraPitch=-30,
                                              cameraTargetPosition=robot_pos)
            

        #     print(f"Step Reward: {reward:.2f}")
        #
        #     if done or truncated:
        #         print("Episode ended early during test loop. Resetting...")
        #         obs, _ = env.reset()

        # -------------------------
        # Custom evaluation of the model
        n_eval_episodes = 3
        episode_rewards = []


        print("\nStarting evaluation over multiple episodes...\n")
        for ep in range(n_eval_episodes):
            ep_rewards = []
            obs, _ = env.reset()
            env.let_robot_fall()
            done = False
            while not done:
                action, _ = model.predict(obs, deterministic=False)
                print(action)
                obs, reward, terminated, truncated, _ = env.step(action)

                ep_rewards.append(reward)
                done = terminated or truncated

            episode_total = ep_rewards[-1]
            episode_rewards.append(episode_total)
            print(f"Episode {ep + 1} Final Reward: {ep_rewards[-1]:.2f}")

        mean_reward = np.mean(episode_rewards)
        std_reward = np.std(episode_rewards)

        print(f"\nEvaluation over {n_eval_episodes} episodes: mean_reward = {mean_reward:.2f} +/- {std_reward:.2f}\n")

        # Clean up
        obs, _ = env.reset()
        env.close()
