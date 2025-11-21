import pybullet as p
import pybullet_data
import time

# Replace this with your actual force variable
force = 15  # example value

# Path to your URDF file
ROBOT_URDF_PATH = f"robots/robot_GEN_15_number_{force}.urdf"

# Connect to PyBullet (GUI or DIRECT)
physics_client = p.connect(p.GUI)  # use p.DIRECT for headless

# Set gravity
p.setGravity(0, 0, -9.8)

# Optionally add a plane
p.setAdditionalSearchPath(pybullet_data.getDataPath())
plane_id = p.loadURDF("plane.urdf")

# Load your robot
start_pos = [0, 0, 0.5]  # Z spawn = 0.5
start_orientation = p.getQuaternionFromEuler([0, 0, 0])
robot_id = p.loadURDF(
    ROBOT_URDF_PATH,
    start_pos,
    start_orientation,
    useFixedBase=False  # free-floating base
)

# Simulation loop
num_steps = 4800
time_step = 1.0 / 240.0  # default PyBullet time step
p.setTimeStep(time_step)

for i in range(num_steps):
    p.stepSimulation()
    # Optional: slow down visualization for GUI
    if i % 10 == 0:
        time.sleep(time_step)

# Disconnect when done
p.disconnect()
