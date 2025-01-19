import pybullet as p
import time
import pybullet_data
import os

from URDFs_set import Random_Generator

physicsClient = p.connect(p.GUI)#or p.DIRECT for non-graphical version

p.setAdditionalSearchPath(pybullet_data.getDataPath()) #optionally

p.setGravity(0,0,-9.8)

planeId = p.loadURDF("plane.urdf") # plane é o plano para o robo ficar e nao continuar a cair


startOrientation = p.getQuaternionFromEuler([0,0,0])


for i in range(10):
    filename = Random_Generator.main(i)

#set the center of mass frame (loadURDF sets base link frame) startPos/Ornp.resetBasePositionAndOrientation(boxId, startPos, startOrientation)
for i in range (600):
    startPos = [0 - i, 0, 1]
    if i < 10:
        print("corrected_robot"+str(i))
        roboID = p.loadURDF("/home/joaoraposo/Documents/GitHub/Evolutionary-Robotics-with-GE/corrected_robot"+str(i)+".urdf",startPos, startOrientation)
    p.stepSimulation()
    time.sleep(1./240.)
cubePos, cubeOrn = p.getBasePositionAndOrientation(roboID)
print(f"AQUI ESTA O PRINT --> {cubePos,cubeOrn}")
p.disconnect()

for i in range(10):
    # Specify the file to be deleted
    file_path = "/home/joaoraposo/Documents/GitHub/Evolutionary-Robotics-with-GE/corrected_robot" + str(i) + ".urdf"
    # Check if the file exists
    if os.path.exists(file_path):
        # Delete the file
        os.remove(file_path)
        print(f"File {file_path} has been deleted.")
    else:
        print(f"File {file_path} does not exist.")
