import pybullet as p
import time
import pybullet_data
import os

# Connect to PyBullet GUI
physicsClient = p.connect(p.GUI)

p.setAdditionalSearchPath(pybullet_data.getDataPath())  # Search for plane.urdf
p.setGravity(0, 0, -9.8)

# Load the ground plane
planeId = p.loadURDF("plane.urdf")

# Robot URDF path
urdf_path = "/home/joaoraposo/Documents/GitHub/Evolutionary-Robotics-with-GE/corrected_robot2.urdf"

# Initial position and orientation
startPos = [0, 0, 1]
startOrientation = p.getQuaternionFromEuler([0, 0, 0])

# Check if URDF file exists
if not os.path.exists(urdf_path):
    print(f"ERROR: URDF file not found: {urdf_path}")
    exit()

# Load the robot with self-collision enabled
roboID = p.loadURDF(urdf_path, startPos, startOrientation, flags=p.URDF_USE_SELF_COLLISION)

# Enable collision detection for all links
num_joints = p.getNumJoints(roboID)
for i in range(num_joints):
    for j in range(i + 1, num_joints):  # Check all pairs
        p.setCollisionFilterPair(roboID, roboID, i, j, enableCollision=True)

# Configure PyBullet Debugging
p.configureDebugVisualizer(p.COV_ENABLE_GUI, 1)
p.configureDebugVisualizer(p.COV_ENABLE_RENDERING, 1)
p.configureDebugVisualizer(p.COV_ENABLE_SHADOWS, 1)

# Improve collision accuracy
p.setPhysicsEngineParameter(enableFileCaching=0)
p.setPhysicsEngineParameter(solverResidualThreshold=1e-8)
p.setPhysicsEngineParameter(numSolverIterations=200)
p.setPhysicsEngineParameter(contactBreakingThreshold=0.001)
p.setPhysicsEngineParameter(enableConeFriction=1)
p.setPhysicsEngineParameter(enableSAT=1)

# Run simulation and check for collisions
print("\n🔍 **Checking Collisions**\n")
for _ in range(500):  # Run for ~2 seconds
    p.stepSimulation()

    # Get all contact points
    contact_points = p.getContactPoints(roboID)

    if contact_points:
        print("🚨 Collision Detected! Links in Contact:")
        for contact in contact_points:
            link_A = contact[3]  # First link ID
            link_B = contact[4]  # Second link ID

            # Get the actual link names
            link_A_name = p.getJointInfo(roboID, link_A)[12].decode("utf-8") if link_A != -1 else "Base"
            link_B_name = p.getJointInfo(roboID, link_B)[12].decode("utf-8") if link_B != -1 else "Base"

            print(f"  🔴 {link_A_name} is colliding with {link_B_name}")

    time.sleep(1.0 / 60.0)  # Slow down simulation

# Print final position
cubePos, cubeOrn = p.getBasePositionAndOrientation(roboID)
print(f"\n✅ Final Base Position: {cubePos}\n")

# Disconnect PyBullet
p.disconnect()
