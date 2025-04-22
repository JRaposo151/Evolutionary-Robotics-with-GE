from stable_baselines3 import PPO
from Env import URDFRobotEnv
import pybullet as p
import random
import torch
import numpy as np


startOrientation = p.getQuaternionFromEuler([0, 0, 0])
startPos = [0, 0, 0.2]
flags = p.URDF_USE_SELF_COLLISION_EXCLUDE_PARENT
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
#torch.device('cuda:'+str(torch.cuda.device_count()) if torch.cuda.is_available() else 'cpu')
print('Using device:', 'cuda' if torch.cuda.is_available() else 'cpu', ', device number:', torch.cuda.device_count(), ', GPUs in system:', torch.cuda.device_count())



for i in range(10):
    print("------------- ------------- ------------- ------------- ")
    print(f'------------- Training Robot number {i} -------------')
    print("------------- ------------- ------------- ------------- ")
    ROBOT_URDF_PATH = f"/home/joaoraposo/Documents/GitHub/Evolutionary-Robotics-with-GE/corrected_robot{0}.urdf"  # ESTE É O ROBO


    env = URDFRobotEnv(ROBOT_URDF_PATH, startPos, startOrientation, flags, render=False)
    env.reset()
    env.let_robot_fall() #TODO NAO PODE ESTAR AQUI MAS NO ENV

    model = PPO(
        policy= 'MlpPolicy',
        env=env,
        learning_rate=0.0003,
        n_steps=2048,
        batch_size=64,
        n_epochs=4,
        gamma=0.999,
        gae_lambda=0.98,
        ent_coef=0.01,
        verbose=0,
        seed=seed
        )


    model.learn(total_timesteps=1000000)

    model.save(f"testVandF_robot{i}")
    #env.save("vec_normalize.pkl")
    env.close()
    break




