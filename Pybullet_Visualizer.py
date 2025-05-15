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
urdf_path = "robots/robot_0.urdf"

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
for _ in range(5000):  # Run for ~2 seconds
    p.stepSimulation()

    time.sleep(1.0 / 60.0)  # Slow down simulation

# Print final position
cubePos, cubeOrn = p.getBasePositionAndOrientation(roboID)
print(f"\n✅ Final Base Position: {cubePos}\n")

# Disconnect PyBullet
p.disconnect()
