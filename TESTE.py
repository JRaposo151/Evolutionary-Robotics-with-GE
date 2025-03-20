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

# Get the number of movable joints in the robot
num_joints = p.getNumJoints(roboID)
print("Number of total joints:", num_joints)

movable_joints = []
movable_joints_revolute = []
movable_joints_continuous = [] # this joint types are revolute but the continuous on the name is because they spin like a wheel

for joint in range(num_joints):
    joint_info = p.getJointInfo(roboID, joint)
    joint_type = joint_info[2]
    print(joint_type)
    lower_limit, upper_limit = joint_info[8:10]
    if lower_limit == -1000 and upper_limit == 1000:
        movable_joints_continuous.append(joint)
        movable_joints.append(joint)
    elif p.getJointInfo(roboID, joint)[2] in [0]: # Joint type: 0=revolute, 1=prismatic, 2=spherical, 3=planar, 4=fixed
        movable_joints_revolute.append(joint)
        movable_joints.append(joint)


# Define action limits for revolute joints (from URDF limits)
revolute_limits_low = [-0.75] * len(movable_joints_revolute)  # Min values for revolute joints (radians)
revolute_limits_high = [0.75] * len(movable_joints_revolute) # Max values for revolute joints (radians)

# Define limits for continuous joints (full rotation allowed)
continuous_limits_low = [-1000] * len(movable_joints_continuous)
continuous_limits_high = [1000] * len(movable_joints_continuous)

# Combine limits: Only keep revolute and continuous joints
low_limits = np.array(revolute_limits_low + continuous_limits_low)
high_limits = np.array(revolute_limits_high + continuous_limits_high)

# Define action space
action_space = spaces.Box(low=low_limits, high=high_limits, dtype=np.float32) #TODO falta o shape

print("Action Space:", action_space)
print("Min Joint Values:", action_space.low)
print("Max Joint Values:", action_space.high)


# Run simulation and command each joint with a sine wave target position
start_time = time.time()
while time.time() - start_time < 20:  # Run for 20 seconds
    action_index = 0  # To track correct action values
    # Sample a random action (within allowed joint limits)
    random_action = action_space.sample()
    #print("Random Action:", random_action)
    for joint in movable_joints:

        joint_info = p.getJointInfo(roboID, joint)
        joint_type = joint_info[2]  # Joint type: 0=revolute, 1=prismatic, 2=spherical, 3=planar, 4=fixed

        if joint_type == p.JOINT_FIXED:
            continue  # Skip fixed joints

        # Compute a target position as a function of time and joint index
        p.setJointMotorControl2(bodyIndex=roboID,
                                jointIndex=joint,
                                controlMode=p.POSITION_CONTROL,
                                targetPosition=random_action[action_index],
                                force=500)
        action_index += 1  # Move to next action value

    p.stepSimulation()
    time.sleep(1. / 240.)

cubePos, cubeOrn = p.getBasePositionAndOrientation(roboID)
print(f"Final base position : {cubePos}")
print(f"Final orientation: {cubeOrn}")

"""EUCLIDIAN DISTANCE para calcular a distancia em linha reta do ponto de partida"""
distance_traveled = math.sqrt((cubePos[0] - startPos[0])**2 +
                              (cubePos[1] - startPos[1])**2 +
                              (cubePos[2] - startPos[2])**2)


print(f"Distance Traveled: {distance_traveled} meters")
p.disconnect()

