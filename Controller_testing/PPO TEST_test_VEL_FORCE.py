import os
import numpy as np
import matplotlib.pyplot as plt
from stable_baselines3 import PPO
from sge_FOR_ER.sge.sge.Env import URDFRobotEnv
import pybullet as p
from stable_baselines3.common.vec_env import VecNormalize, DummyVecEnv

forces = [0.5]
velocities = [5]


def URDFRobotEnv_make(ROBOT_URDF_PATH, velocity, force, render, plane):
    def _init():
        env = URDFRobotEnv(ROBOT_URDF_PATH, velocity, force, render=render, plane=plane)
        return env
    return _init

# Open the file for writing evaluation results
# Run evaluation for robots
for force in forces:
    for velocity in velocities:

        vec_path_2 = f"/home/joaoraposo/Documents/GitHub/Evolutionary-Robotics-with-GE/robots_test/best_gen_020.pkl"
        ROBOT_URDF_PATH = f"/home/joaoraposo/Documents/GitHub/Evolutionary-Robotics-with-GE/robots_test/best_gen_020.urdf"
        model_name = f"/home/joaoraposo/Documents/GitHub/Evolutionary-Robotics-with-GE/robots_test/best_gen_020.zip"


        env = DummyVecEnv([URDFRobotEnv_make(ROBOT_URDF_PATH, velocity=5, force=0.5,  render=True, plane=0)])
        env_vec = VecNormalize.load(vec_path_2, env)
            #  do not update them at test time
        env_vec.training = False
            # reward normalization is not needed at test time
        env_vec.norm_reward = False

        model = PPO.load(model_name)
            # Set camera to follow the robot

            # Custom evaluation of the model
        n_eval_episodes = 3
        episode_rewards = []
        raw_env = env_vec.envs[0]

        print("\nStarting evaluation over multiple episodes...\n")
        for ep in range(n_eval_episodes):

            ep_rewards = []
            obs = env_vec.reset()
            raw_env.let_robot_fall()
            done = False
            while not done:
                action, _ = model.predict(obs, deterministic=False)
                obs, reward, terminated, _ = env_vec.step(action)
                    #print(reward)
                ep_rewards.append(reward)
                robot_pos = raw_env.getRobotPosition()
                p.resetDebugVisualizerCamera(cameraDistance=1,
                                                 cameraYaw=50,
                                                 cameraPitch=-30,
                                                 cameraTargetPosition=robot_pos)
                done = terminated

            episode_total = ep_rewards[-1][0]
            episode_rewards.append(episode_total)
            print(f"Episode {ep + 1} Final Reward: {episode_total:.2f}")

        mean_reward = np.mean(episode_rewards)
        std_reward = np.std(episode_rewards)

        print(f"\nEvaluation over {n_eval_episodes} episodes: mean_reward = {mean_reward:.2f} +/- {std_reward:.2f}\n")

        # Clean up
        obs= env_vec.reset()
        env_vec.close()
