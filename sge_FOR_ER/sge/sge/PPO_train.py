import os
from stable_baselines3 import PPO
from sge_FOR_ER.sge.sge.Env import URDFRobotEnv
import pybullet as p
import random
import torch
import numpy as np
from stable_baselines3.common.vec_env import VecNormalize, DummyVecEnv, SubprocVecEnv


def URDFRobotEnv_make(ROBOT_URDF_PATH, velocity, force, render, plane):
    def _init():
        env = URDFRobotEnv(ROBOT_URDF_PATH, velocity, force, plane, render=render)
        return env
    return _init

def train(PATH, name, n_generation, plane):
    output_folder_brains = "robots_brains/"
    output_folder_vec = "robots_vec/"
    # Ensure the output folder exists
    os.makedirs(output_folder_brains, exist_ok=True)
    os.makedirs(output_folder_vec, exist_ok=True)
    model_path = os.path.join(output_folder_brains, f"{name}.zip")

    if not os.path.exists(model_path):


        # # Check if CUDA is available
        # if torch.cuda.is_available():
        #     print("CUDA is available! You can use the GPU.")
        # else:
        #     print("CUDA is not available. You are using the CPU.")
        #
        # # Get number of GPUs available
        # print(f"GPUs available: {torch.cuda.device_count()}")

        """
        ATIVAÇÃO DE CUDA AQUI 
        """
        print('Using device:', 'cuda' if torch.cuda.is_available() else 'cpu', ', device number:',
              torch.cuda.device_count(), ', GPUs in system:', torch.cuda.device_count())

        n_envs = 4
        env = [URDFRobotEnv_make(PATH, velocity=5, force=0.5, render=False, plane=plane) for _ in range(n_envs)]
        env = DummyVecEnv(env)  # Or use DummyVecEnv if you have debugging needs
        env = VecNormalize(env, training=True, norm_obs=True, norm_reward=True, clip_obs=10.0)
        model = PPO(
                    policy='MlpPolicy',
                    env=env,
                    learning_rate=0.0003,
                    n_steps=2048,
                    batch_size=64,
                    n_epochs=10,
                    gamma=0.99,
                    gae_lambda=0.95,
                    verbose=1,
                    tensorboard_log="./logs_1/",
                    seed=42,
                    device="cuda" if torch.cuda.is_available() else "cpu",

        )
        if (100000 * n_envs + (50000 * n_generation) < 1000000):
            total_timesteps = 100000 * n_envs + (50000 * n_generation)
        else:
            total_timesteps = 1000000
        model.learn(total_timesteps=total_timesteps)
        model.save(model_path)


        model_path = os.path.join(output_folder_vec, f"{name}.pkl")
        env.save(model_path)
        p.disconnect()
        env.close()



