import numpy as np
import pybullet as p
import pybullet_data
import time


# Start PyBullet in GUI mode
physicsClient = p.connect(p.GUI)
p.setAdditionalSearchPath(pybullet_data.getDataPath())
p.setGravity(0, 0, -9.81)
startPos = [0, 0, 0.5]
startOrientation = p.getQuaternionFromEuler([0, 0, 0])
flags = p.URDF_USE_SELF_COLLISION_EXCLUDE_PARENT
p.loadURDF("plane.urdf")
p.setPhysicsEngineParameter(enableFileCaching=0)  # Avoid caching old URDFs
p.setPhysicsEngineParameter(enableConeFriction=1)  # Improve friction
p.setPhysicsEngineParameter(enableSAT=1)  # Use SAT solver for better collisions

# Load the robot
robots = 10

# Function to move a joint back and forth
def test_joint(joint_index):
    print(f"\nTesting Joint {joint_index}...")

    for _ in range(1000):
        p.stepSimulation()
        time.sleep(1.0 / 240.0)  # Small delay for real-time visualization

    for _ in range(3):  # Repeat motion 3 times
        # Move to max position
        p.setJointMotorControl2(robot_id, joint_index, p.VELOCITY_CONTROL, targetVelocity=10)
        for _ in range(1000):
            p.stepSimulation()
            time.sleep(1.0 / 240.0)

        # Move to min position
        p.setJointMotorControl2(robot_id, joint_index, p.VELOCITY_CONTROL, targetVelocity=-10)
        for _ in range(1000):
            p.stepSimulation()
            time.sleep(1.0 / 240.0)


# Test each joint one by one
for i in range(0,robots):

    robot_path = f"/home/joaoraposo/Documents/GitHub/Evolutionary-Robotics-with-GE/corrected_robot{i}.urdf"
    robot_id = p.loadURDF(robot_path, startPos, startOrientation, useFixedBase=False, flags=flags)

    # Get number of joints
    num_joints = p.getNumJoints(robot_id)
    print(f"::::::::::::::::::::::::NEW ROBOT {i} TESTING JOINTS::::::::::::::::::::::::")
    print(f"Number of Joints: {num_joints}\n")


    # Identify Movable Joints
    numJoints = p.getNumJoints(robot_id)
    movable_joints = []

    for joint in range(numJoints):
        joint_info = p.getJointInfo(robot_id, joint)
        if p.getJointInfo(robot_id, joint)[2] in [0]:
            movable_joints.append(joint)

    num_movable_joints = len(movable_joints)
    print(f"Number of Movable Joints: {num_movable_joints}")

    for joint in movable_joints:
        test_joint(joint)
    # Remove the robot from simulation
    print(f"\n🗑️ Removing Robot {i}\n")
    p.removeBody(robot_id)
    time.sleep(1)  # Small delay before loading the next robot

print("\nJoint Testing Complete!")
