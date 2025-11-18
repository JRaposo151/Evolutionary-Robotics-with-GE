import pybullet as p
import pybullet_data
import time


# Function to move a joint back and forth
def test_joint(joint_index, roboID):
    print(f"\nTesting Joint {joint_index}...")

    forces = [0.5]
    velocities = [5]

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
            p.setJointMotorControl2(roboID, joint, p.TORQUE_CONTROL, force=forces[0])
        else:
            print("JOINT REVOLUTE NESTE MOMENTO A MEXER-SE POSITIVAMENTE")
            p.setJointMotorControl2(roboID, joint, p.POSITION_CONTROL, targetPosition=0.75, targetVelocity=velocities[0],force=forces[0])  # normal speed is 2.0 radians/s and force is 10
        for _ in range(10000):
            p.stepSimulation()
        print("ACABOUUUUU")
        time.sleep(1.0 / 240.0)

        if "continuous" in type_str:
            print("JOINT CONTINUOUS NESTE MOMENTO A MEXER-SE NEGATIVAMENTE")
            p.setJointMotorControl2(roboID, joint, p.VELOCITY_CONTROL, force=0.000)
            p.setJointMotorControl2(roboID, joint, p.TORQUE_CONTROL, force=-forces[0])
        else:
            print("JOINT REVOLUTE NESTE MOMENTO A MEXER-SE NEGATIVAMENTE")
            p.setJointMotorControl2(roboID, joint, p.POSITION_CONTROL, targetPosition=-0.75, targetVelocity=velocities[0],force=forces[0])  # normal speed is 2.0 radians/s and force is 10

        for _ in range(8000):
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

    robot_path = f"robots_ind/best_gen_020.urdf"
    robot_id = p.loadURDF(robot_path, basePosition=[0, 0, 0.5], useFixedBase=True, flags=p.URDF_USE_SELF_COLLISION)

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

    for i in range(p.getNumJoints(robot_id)):
        joint_info = p.getJointInfo(robot_id, i)
        link_name = joint_info[12].decode("utf-8")

        # Disable ALL collisions for links that are just visual joints
        if "L_joint_" in link_name or "Sphere_" in link_name or "B_joint" in link_name:
            link_index = joint_info[0]
            p.setCollisionFilterGroupMask(robot_id, link_index, collisionFilterGroup=0, collisionFilterMask=0)

    for joint in movable_joints:
        test_joint(joint, robot_id)
    # Remove the robot from simulation
    print(f"\n🗑️ Removing Robot {i}\n")
    p.removeBody(robot_id)
    time.sleep(1)  # Small delay before loading the next robot

print("\nJoint Testing Complete!")
