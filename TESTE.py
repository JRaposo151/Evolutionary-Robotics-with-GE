import pybullet as p
import time
import pybullet_data
import os

from URDFs_set import Autonomous_Assembly

physicsClient = p.connect(p.GUI)#or p.DIRECT for non-graphical version

p.setAdditionalSearchPath(pybullet_data.getDataPath()) #optionally

p.setGravity(0,0,-9.8)

planeId = p.loadURDF("plane.urdf") # plane é o plano para o robo ficar e nao continuar a cair


startOrientation = p.getQuaternionFromEuler([0,0,0])


#set the center of mass frame (loadURDF sets base link frame) startPos/Ornp.resetBasePositionAndOrientation(boxId, startPos, startOrientation)

startPos = [0, 0, 1]

i = 2

for x in range (60000):
    urdf_path = f"/home/joaoraposo/Documents/GitHub/Evolutionary-Robotics-with-GE/corrected_robot{i}.urdf"
    if not os.path.exists(urdf_path):
        print(f"ERROR: URDF file not found: {urdf_path}")
    else:
        roboID = p.loadURDF(urdf_path, startPos, startOrientation, useFixedBase=False   )
        p.changeDynamics(roboID, -1, mass=1.0)  # Ensure it's not static
    p.stepSimulation()
    time.sleep(1./240.)
cubePos, cubeOrn = p.getBasePositionAndOrientation(roboID)
print(f"AQUI ESTA O PRINT --> {cubePos,cubeOrn}")
p.disconnect()

