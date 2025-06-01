import pybullet as p
import time
import pybullet_data
import os

# Connect to PyBullet GUI
physicsClient = p.connect(p.GUI)

p.setAdditionalSearchPath(pybullet_data.getDataPath())  # Search for plane.urdf
p.setGravity(0, 0, -10)

# Load the ground plane
planeId = p.loadURDF("plane.urdf")

# Robot URDF path
urdf_path = "/home/joaoraposo/Documents/GitHub/Evolutionary-Robotics-with-GE/sge_FOR_ER/sge/examples/robots/robot_GEN_0_number_0.urdf"

# Initial position and orientation
startPos = [0, 0, 0.5]
startOrientation = p.getQuaternionFromEuler([0, 0, 0])

# Check if URDF file exists
if not os.path.exists(urdf_path):
    print(f"ERROR: URDF file not found: {urdf_path}")
    exit()

# Load the robot with self-collision enabled
roboID = p.loadURDF(urdf_path, startPos, startOrientation, flags=p.URDF_USE_SELF_COLLISION)


# Run simulation and check for collisions
print("\n🔍 **Checking Collisions**\n")
for i in range(p.getNumJoints(roboID)):
    joint_info = p.getJointInfo(roboID, i)
    link_name = joint_info[12].decode("utf-8")

    # Disable ALL collisions for links that are just visual joints
    if "L_joint_" in link_name or "Sphere_" in link_name or "B_joint" in link_name:
        link_index = joint_info[0]
        p.setCollisionFilterGroupMask(roboID, link_index, collisionFilterGroup=0, collisionFilterMask=0)

for r in range(5000):  # Run for ~2 seconds
    p.stepSimulation()
    if r > 500:
        print()
        robot_position, ori = p.getBasePositionAndOrientation(roboID)
        print(robot_position)
        print(ori)
        lin_vel, ang_vel = p.getBaseVelocity(roboID)
        print( lin_vel, ang_vel)
    time.sleep(1.0 / 60.0)  # Slow down simulation

# Print final position
cubePos, cubeOrn = p.getBasePositionAndOrientation(roboID)
print(f"\n✅ Final Base Position: {cubePos}\n")

# Disconnect PyBullet
p.disconnect()
