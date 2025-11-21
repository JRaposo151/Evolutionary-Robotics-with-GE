import os
import numpy as np
import matplotlib.pyplot as plt
from stable_baselines3 import PPO
from sge_FOR_ER.sge.sge.Env import URDFRobotEnv
from sge_FOR_ER.sge.sge import PPO_train
import pybullet as p

from stable_baselines3.common.vec_env import VecNormalize, DummyVecEnv
"""
:::::::::::::::::: EVALUATE THE ROBOT AND ITS CONTROLLER :::::::::::::::::: 
"""
# Ensure results directory exists
results_dir = "evaluation_results"
os.makedirs(results_dir, exist_ok=True)




def URDFRobotEnv_make(ROBOT_URDF_PATH, render):
    def _init():
        env = URDFRobotEnv(ROBOT_URDF_PATH, 5, 0.5, plane = 0, render=render)
        return env
    return _init


forces = ['010']
# Open the file for writing evaluation results
with open(os.path.join(results_dir, "evaluation_results_TESTES_velocidade_Força.txt"), 'w') as f:
    name = 0
    f.write("Evaluation Results:\n\n")
    # Run evaluation for robots
    for force in forces:
        print("------------- ------------- ------------- ------------- ")
        print(f"------------- Evaluating Robot number {force} Force {0.5}  Velocity {5} -------------")
        print("------------- ------------- ------------- ------------- ")

        vec_path_2 = f"robots_ind/best_gen_{force}.pkl"
        ROBOT_URDF_PATH = f"robots_ind/best_gen_{force}.urdf"
        model_name = f"robots_ind/best_gen_{force}"

        # # Ensure the model file exists
        # if not os.path.exists(model_name):
        #     print(f"Model {model_name} not found. Skipping...")
        #     continue
        env = DummyVecEnv([URDFRobotEnv_make(ROBOT_URDF_PATH, render=True)])
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
