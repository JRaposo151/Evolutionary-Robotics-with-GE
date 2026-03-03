from stable_baselines3 import PPO
#from Env_plane_1 import URDFRobotEnv
from Env_plane_2_VELO_CONTROL import URDFRobotEnv

import random
import torch
import numpy as np
import os
from stable_baselines3.common.vec_env import VecNormalize, DummyVecEnv, SubprocVecEnv

save_folder = "models_PPO_Test_NEW_REWARD"
#save_folder = "models_PPO_Test"
os.makedirs(save_folder, exist_ok=True)


seed = 43
random.seed(seed)
np.random.seed(seed)
torch.manual_seed(seed)


# Check if CUDA is available
if torch.cuda.is_available():
    print("CUDA is available! You can use the GPU.")
else:
    print("CUDA is not available. You are using the CPU.")


#print("\n ************************")
#print(torch.version.cuda)
#print("\************************n")

# Get number of GPUs available
print(f"GPUs available: {torch.cuda.device_count()}")

# Print information about the GPUs
# for i in range(torch.cuda.device_count()):
#     print(f"GPU {i}: {torch.cuda.get_device_name(i)}")

"""
ATIVAÇÃO DE CUDA AQUI 
"""
print('Using device:', 'cuda' if torch.cuda.is_available() else 'cpu', ', device number:', torch.cuda.device_count(), ', GPUs in system:', torch.cuda.device_count())


forces = [15]
velocities = [2]

def URDFRobotEnv_make(ROBOT_URDF_PATH, velocity, force, render,plane):
    def _init():
        env = URDFRobotEnv(ROBOT_URDF_PATH, velocity, force, render=render, plane=plane)
        return env
    return _init

for force in forces:
    for velocity in velocities:
        if not os.path.exists(f"models_PPO_Test/testVansdF_roboooooooooot_VELO_{velocity}_FORCE_{force}.zip"):

            print("------------- ------------- ------------- ------------- ")
            print(f'------------- Training Robot number {velocity} -------------')
            print("------------- ------------- ------------- ------------- ")
            ROBOT_URDF_PATH_sim = f"./models_PPO_Test_NEW_REWARD/best_gen_020_simetrico_geracoes.urdf"  # ESTE É O ROBO
            ROBOT_URDF_PATH = f"./models_PPO_Test_NEW_REWARD/best_gen_020_POSITION_CONTROL.urdf"  # ESTE É O ROBO

            husky = "husky/husky.urdf"

            print(":::::VELOCITY:", 67)
            print(":::::FORCE:", force)
            env = [URDFRobotEnv_make(ROBOT_URDF_PATH, 67, force, render = False, plane= 0)]
            #env = SubprocVecEnv(env)
            env = DummyVecEnv(env)  # Or use DummyVecEnv if you have debugging needs
            env = VecNormalize(env, training=True, norm_obs=True, norm_reward=True)

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
                    seed=seed,
                    device= "cuda" if torch.cuda.is_available() else "cpu",
                    )
            if velocity == 1:
                model.learn(total_timesteps=1000000)
            elif velocity == 2:
                model.learn(total_timesteps=300000)


            # turn 0.05 → "0_05", 0.1 → "0_1", 1.0 → "1_0" (or "1" if you prefer)
            force_str = str(force).rstrip('0').rstrip('.')  # e.g. "0.05"→"0.05"; "1.0"→"1"
            force_str = force_str.replace('.', '_')  # e.g. "0.05"→"0_05"

            if velocity == 1:
                model_path = os.path.join(save_folder, f"best_gen_020_new_list_timesteps_240_1m")
                model.save(model_path)
                model_path = os.path.join(save_folder, f"best_gen_020_new_list_timesteps_240_1m.pkl")
                env.save(model_path)
                env.close()
            elif velocity == 2:
                #model_path = os.path.join(save_folder, f"best_gen_020_sem_castigo_distancia_tStep_horizontal")
                model_path = os.path.join(save_folder, f"best_gen_020_rodas_e_revolute_com_castigo_distancia_tStep_horizontal")

                model.save(model_path)
                #model_path = os.path.join(save_folder, f"best_gen_020_sem_castigo_distancia_tStep_horizontal.pkl")
                model_path = os.path.join(save_folder, f"best_gen_020_rodas_e_revolute_com_castigo_distancia_tStep_horizontal.pkl")

                env.save(model_path)
                env.close()