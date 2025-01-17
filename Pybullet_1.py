import pybullet as p
import time
import pybullet_data

physicsClient = p.connect(p.GUI)#or p.DIRECT for non-graphical version

p.setAdditionalSearchPath(pybullet_data.getDataPath()) #optionally

p.setGravity(0,0,-9.8)

planeId = p.loadURDF("plane.urdf") # plane é o plano para o robo ficar e nao continuar a cair

startPos = [0,0,1]

startOrientation = p.getQuaternionFromEuler([0,0,0])

roboID = p.loadURDF("/home/joaoraposo/Documents/GitHub/Evolutionary-Robotics-with-GE/URDFs_set/custom_robot.urdf",startPos, startOrientation) #r2d2.urdf   planar_2R_robot.urdf

#set the center of mass frame (loadURDF sets base link frame) startPos/Ornp.resetBasePositionAndOrientation(boxId, startPos, startOrientation)
for i in range (100000):
    p.stepSimulation()
    time.sleep(1./240.)
cubePos, cubeOrn = p.getBasePositionAndOrientation(roboID)
print(f"AQUI ESTA O PRINT --> {cubePos,cubeOrn}")
p.disconnect()
