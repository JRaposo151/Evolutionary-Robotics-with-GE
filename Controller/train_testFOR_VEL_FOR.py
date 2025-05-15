from stable_baselines3 import PPO
from Env import URDFRobotEnv
import random
import torch
import numpy as np
import os
from stable_baselines3.common.vec_env import VecNormalize, DummyVecEnv, SubprocVecEnv

save_folder = "models_PPO_Test_NEW_REWARD"
#save_folder = "models_PPO_Test"
os.makedirs(save_folder, exist_ok=True)


seed = 10
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


name = 0
forces = [0.5]
velocities = [5]

def URDFRobotEnv_make(ROBOT_URDF_PATH, render):
    def _init():
        env = URDFRobotEnv(ROBOT_URDF_PATH, velocity, force, render=render)
        return env
    return _init

for force in forces:
    for velocity in velocities:
        print(f"testVandF_roobot{name}_VELO_{velocity}_FORCE_{force}.zip")
        if not os.path.exists(f"models_PPO_Test/testVandF_robootDEFAULT2{name}_VELO_{velocity}_FORCE_{force}.zip"):

            print("------------- ------------- ------------- ------------- ")
            print(f'------------- Training Robot number {name} -------------')
            print("------------- ------------- ------------- ------------- ")
            ROBOT_URDF_PATH = f"../robots/robot_{name}.urdf"  # ESTE É O ROBO


            print(":::::VELOCITY:", velocity)
            print(":::::FORCE:", force)
            env = [URDFRobotEnv_make(ROBOT_URDF_PATH, render = False)]
            #env = SubprocVecEnv(env)
            env = DummyVecEnv(env)  # Or use DummyVecEnv if you have debugging needs
            env = VecNormalize(env, training=True, norm_obs=True, norm_reward=True, clip_obs=10.0)

            model = PPO(
                    policy='MlpPolicy',
                    env=env,
                    learning_rate=0.0003,
                    n_steps=2048,
                    batch_size=64,
                    n_epochs=4,
                    gamma=0.99,
                    gae_lambda=0.95,
                    ent_coef=0.01,
                    verbose=1,
                    seed=seed
                    )

            model.learn(total_timesteps=1000000)

            # turn 0.05 → "0_05", 0.1 → "0_1", 1.0 → "1_0" (or "1" if you prefer)
            force_str = str(force).rstrip('0').rstrip('.')  # e.g. "0.05"→"0.05"; "1.0"→"1"
            force_str = force_str.replace('.', '_')  # e.g. "0.05"→"0_05"
            model_path = os.path.join(save_folder, f"testVandF_robootDEFAULT2{name}_VELO_{velocity}_FORCE_{force_str}")
            model.save(model_path)
            model_path = os.path.join(save_folder, f"testVandF_robootDEFAULT2{name}_VELO_{velocity}_FORCE_{force_str}.pkl")
            env.save(model_path)
            env.close()
