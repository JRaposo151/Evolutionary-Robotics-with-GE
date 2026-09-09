from stable_baselines3 import PPO
#from Env_plane_1 import URDFRobotEnv
from sge_FOR_ER.sge.sge.Env_mars import URDFRobotEnv

import random
import torch
import numpy as np
import os
from stable_baselines3.common.vec_env import VecNormalize, DummyVecEnv, SubprocVecEnv

#save_folder = "models_PPO_Test_NEW_REWARD"
save_folder = "Husky_like_robot&controllers"
os.makedirs(save_folder, exist_ok=True)



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

def URDFRobotEnv_make(ROBOT_URDF_PATH, velocity, force, render):
    def _init():
        env = URDFRobotEnv(ROBOT_URDF_PATH, velocity, force, render=render)
        return env
    return _init

for force in forces:
    for velocity in velocities:
        if not os.path.exists(f"models_PPO_Test/testVansdF_roboooooooooot_VELO_{velocity}_FORCE_{force}.zip"):

            #ROBOT_URDF_PATH = f"./Husky_like_robot&controllers/best_gen_020_1.urdf"
            print("------------- ------------- ------------- ------------- ")
            print(f'------------- Training Robot number {velocity} -------------')
            print("------------- ------------- ------------- ------------- ")


            vec_path_2 = f"/home/joaoraposo/Desktop/Resultados_ANYDESK/95cross_5mut/mars_S_42/robots_ind/best_gen_007_new.pkl"
            ROBOT_URDF_PATH = f"/home/joaoraposo/Desktop/Resultados_ANYDESK/95cross_5mut/mars_S_42/robots_ind/best_gen_007.urdf"
            model_name = f"/home/joaoraposo/Desktop/Resultados_ANYDESK/95cross_5mut/mars_S_42/robots_ind/best_gen_007_new"

            env = [URDFRobotEnv_make(ROBOT_URDF_PATH, 67, force, render = False)]
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
                    seed=42,
                    device= "cuda" if torch.cuda.is_available() else "cpu",
                    )
            if velocity == 1:
                model.learn(total_timesteps=1000000)
            elif velocity == 2:
                try:
                    model.learn(total_timesteps=170000)
                except Exception as e:
                    print(e)

            # turn 0.05 → "0_05", 0.1 → "0_1", 1.0 → "1_0" (or "1" if you prefer)
            force_str = str(force).rstrip('0').rstrip('.')  # e.g. "0.05"→"0.05"; "1.0"→"1"
            force_str = force_str.replace('.', '_')  # e.g. "0.05"→"0_05"

            if velocity == 1:
                model_path = os.path.join(save_folder, f"husk_like_horizontal")
                model.save(model_path)
                model_path = os.path.join(save_folder, f"husk_like_horizontal.pkl")
                env.save(model_path)
                env.close()
            elif velocity == 2:
                #model_path = os.path.join(save_folder, f"husk_like_horizontal")
                #model_path = os.path.join(save_folder, f"best_gen_020_com_castigo_exponencial_fixed_marte")

                model.save(model_name)
                #vec_path_2 = os.path.join(save_folder, f"husk_like_horizontal.pkl")
                #vec_path_2 = os.path.join(save_folder, f"best_gen_020_com_castigo_exponencial_fixed_marte.pkl")

                env.save(vec_path_2)
                env.close()