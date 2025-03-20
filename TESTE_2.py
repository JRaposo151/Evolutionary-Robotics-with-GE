import pybullet as p
import pybullet_data
import time

# Start PyBullet in GUI mode
physicsClient = p.connect(p.GUI)
p.setAdditionalSearchPath(pybullet_data.getDataPath())
p.setGravity(0, 0, -9.81)

# Load the robot
i = 0
robot_path = f"/home/joaoraposo/Documents/GitHub/Evolutionary-Robotics-with-GE/corrected_robot{i}.urdf"
robot_id = p.loadURDF(robot_path, basePosition=[0, 0, 0.5], useFixedBase=True)

# Get number of joints
num_joints = p.getNumJoints(robot_id)
print(f"Number of Joints: {num_joints}\n")

# Print joint details
for i in range(num_joints):
    joint_info = p.getJointInfo(robot_id, i)
    joint_name = joint_info[1].decode('utf-8')
    joint_type = joint_info[2]
    print(f"Joint {i}: {joint_name} | Type: {joint_type}")


# Function to move a joint back and forth
def test_joint(joint_index):
    print(f"\nTesting Joint {joint_index}...")

    for _ in range(3):  # Repeat motion 3 times
        # Move to max position
        p.setJointMotorControl2(robot_id, joint_index, p.POSITION_CONTROL, targetPosition=1.0)
        for _ in range(100):
            p.stepSimulation()
            time.sleep(1.0 / 240.0)

        # Move to min position
        p.setJointMotorControl2(robot_id, joint_index, p.POSITION_CONTROL, targetPosition=-1.0)
        for _ in range(100):
            p.stepSimulation()
            time.sleep(1.0 / 240.0)


# Test each joint one by one
for joint in range(num_joints):
    test_joint(joint)

print("\nJoint Testing Complete!")
