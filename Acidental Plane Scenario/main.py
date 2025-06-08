import pybullet as p
import pybullet_data
import numpy as np
import time

# Connect to PyBullet GUI
p.connect(p.GUI)
p.setAdditionalSearchPath(pybullet_data.getDataPath())
p.resetSimulation()

heightData = np.loadtxt("../sge_FOR_ER/sge/examples/terrain_data.csv", delimiter=',')

terrainSize = 256  # Assuming the terrain is 256x256
        
heightfieldData = heightData.flatten()  # Flatten to be applied on the PyBullet's function createCollisionShape
    
# Create the terrain shape 
terrainShape = p.createCollisionShape(
    shapeType=p.GEOM_HEIGHTFIELD,
    meshScale=[2.8, 2.8, 40.0],   # Scale the terrain size and height
    heightfieldTextureScaling=terrainSize / 2,
    heightfieldData=heightfieldData,
    numHeightfieldRows=terrainSize,
    numHeightfieldColumns=terrainSize
)
    
# Create the terrain object
terrainId = p.createMultiBody(0, terrainShape)
p.resetBasePositionAndOrientation(terrainId, [0, 0, 8.5], [0, 0, 0, 1]) # Position
p.changeVisualShape(terrainId, -1, rgbaColor=[1, 1, 1, 1])            # Color

# Set the friction coefficient of the terrain
p.changeDynamics(terrainId, -1, lateralFriction=1.0)

p.setGravity(0, 0, -1.62)

p.loadURDF("r2d2.urdf", [0, 0, -0.2], p.getQuaternionFromEuler([0, 0, 0]))

while True:
    p.stepSimulation()
    time.sleep(1.0 / 240)