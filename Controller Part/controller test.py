import gym
import pybullet as p
import time
import pybullet_data
import os
import math
import numpy as np
from gym import spaces

# Connect to PyBullet GUI
p.connect(p.GUI)
p.connect(p.DIRECT)
p.setAdditionalSearchPath(pybullet_data.getDataPath())
p.setGravity(0, 0, -9.8)
planeId = p.loadURDF("plane.urdf")

startOrientation = p.getQuaternionFromEuler([0, 0, 0])
startPos = [0, 0, 0.2]

# Robot path, modify to get all the robot instead of just one TODO
i = 0
urdf_path = f"/home/joaoraposo/Documents/GitHub/Evolutionary-Robotics-with-GE/corrected_robot{i}.urdf"
if not os.path.exists(urdf_path):
    print(f"ERROR: URDF file not found: {urdf_path}")
else:
    roboID = p.loadURDF(urdf_path, startPos, startOrientation, useFixedBase=False)
    p.changeDynamics(roboID, -1, mass=1.0)


# Create the env
env = gym.make(urdf_path)

# Get the state space and action space
s_size = env.observation_space.shape
a_size = env.action_space

print(s_size, a_size)