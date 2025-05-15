import pybullet as p
import pybullet_data
import time


# Function to move a joint back and forth
def test_joint(joint_index, roboID):
    print(f"\nTesting Joint {joint_index}...")

    forces = [5, 10, 20, 30]
    velocities = [2, 5, 8, 10, 15]

    for _ in range(1000):
        p.stepSimulation()
        time.sleep(1.0 / 240.0)  # Small delay for real-time visualization

    for _ in range(3):  # Repeat motion 3 times
        # Move to max position
        joint_info = p.getJointInfo(roboID, joint)
        type = joint_info[12]

        type_str = type.decode("utf-8")
        if "continuous" in type_str:
            print("JOINT CONTINUOUS NESTE MOMENTO A MEXER-SE POSITIVAMENTE")
            p.setJointMotorControl2(roboID, joint, p.VELOCITY_CONTROL, force=0.000)
            p.setJointMotorControl2(roboID, joint, p.TORQUE_CONTROL, force=forces[2])
        else:
            print("JOINT REVOLUTE NESTE MOMENTO A MEXER-SE POSITIVAMENTE")
            p.setJointMotorControl2(roboID, joint, p.POSITION_CONTROL, targetPosition=0.75, targetVelocity=velocities[0],force=forces[0])  # normal speed is 2.0 radians/s and force is 10
        for _ in range(1000):
            p.stepSimulation()
            time.sleep(1.0 / 240.0)
        print("ACABOUUUUU")

        if "continuous" in type_str:
            print("JOINT CONTINUOUS NESTE MOMENTO A MEXER-SE NEGATIVAMENTE")
            p.setJointMotorControl2(roboID, joint, p.VELOCITY_CONTROL, force=0.000)
            p.setJointMotorControl2(roboID, joint, p.TORQUE_CONTROL, force=-forces[0])
        else:
            print("JOINT REVOLUTE NESTE MOMENTO A MEXER-SE NEGATIVAMENTE")
            p.setJointMotorControl2(roboID, joint, p.POSITION_CONTROL, targetPosition=-0.75, targetVelocity=velocities[0],force=forces[0])  # normal speed is 2.0 radians/s and force is 10

        for _ in range(1000):
            p.stepSimulation()
            time.sleep(1.0 / 240.0)


# Start PyBullet in GUI mode
physicsClient = p.connect(p.GUI)
p.setAdditionalSearchPath(pybullet_data.getDataPath())
p.setGravity(0, 0, -9.81)

# Load the robot
robots = 1


# Test each joint one by one
for i in range(0,robots):

    robot_path = f"../robots/robot_0.urdf"
    robot_id = p.loadURDF(robot_path, basePosition=[0, 0, 0.5], useFixedBase=True)

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
        test_joint(joint, robot_id)
    # Remove the robot from simulation
    print(f"\n🗑️ Removing Robot {i}\n")
    p.removeBody(robot_id)
    time.sleep(1)  # Small delay before loading the next robot

print("\nJoint Testing Complete!")
