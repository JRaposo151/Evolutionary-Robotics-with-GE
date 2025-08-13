import os
import time
import pybullet as p
import pybullet_data
import numpy as np
import gymnasium as gym



class URDFRobotEnv(gym.Env):
    def __init__(self,
                 urdf_path,
                 v,
                 f,
                 plane,
                 render=False,
                 ):

        #super is to ensure that Gym's built-in functionalities are properly initialized.
        """
        :param urdf_path: the path of the robot that we need to train
        :param render: determines whether the simulation will display a visual window (p.GUI) or run in headless mode (p.DIRECT).

        Why do we use super()?
            - Ensures that the URDFRobotEnv class inherits all necessary behavior from gym.Env.
            - Allows gym.Env to manage things like resetting, stepping, and rendering properly.
            - If we don't use super(), Gym might not recognize the environment correctly when training with PPO.
        """
        super(URDFRobotEnv, self).__init__()

        self.flags = p.URDF_USE_SELF_COLLISION
        self.urdf_path = urdf_path
        self.render_mode = render
        self.start_position = np.array([0, 0, 0.5])  # Store starting position
        self.start_orientation = np.array(p.getQuaternionFromEuler([0, 0, 0]))
        self.f = f
        self.v = v
        self.plane = plane
        # Connect to PyBullet
        if self.render_mode:
            p.connect(p.GUI)
        else:
            p.connect(p.DIRECT)

        p.setAdditionalSearchPath(pybullet_data.getDataPath())
        p.setPhysicsEngineParameter(enableFileCaching=0)  # Avoid caching old URDFs
        # Show contact points in PyBullet
        p.setPhysicsEngineParameter(enableConeFriction=1)  # Improve friction
        p.setPhysicsEngineParameter(enableSAT=1)  # Use SAT solver for better collisions

        p.setGravity(0, 0, -9.8)
        if self.plane==0:
            p.loadURDF("plane.urdf")
        else:
            heightData = np.loadtxt("../examples/terrain_data.csv", delimiter=',')
            terrainSize = 256  # Assuming the terrain is 256x256
            heightfieldData = heightData.flatten()  # Flatten to be applied on the PyBullet's function createCollisionShape

            # Create the terrain shape
            terrainShape = p.createCollisionShape(
                shapeType=p.GEOM_HEIGHTFIELD,
                meshScale=[2.8, 2.8, 40.0],  # Scale the terrain size and height
                heightfieldTextureScaling=terrainSize / 2,
                heightfieldData=heightfieldData,
                numHeightfieldRows=terrainSize,
                numHeightfieldColumns=terrainSize
            )

            # Create the terrain object
            self.terrainId =  p.createMultiBody(0, terrainShape)
            p.resetBasePositionAndOrientation(self.terrainId , [0, 0, 8.5], [0, 0, 0, 1])  # Position
            p.changeVisualShape(self.terrainId, -1, rgbaColor=[1, 1, 1, 1])  # Color

            # Set the friction coefficient of the terrain
            p.changeDynamics(self.terrainId, -1, lateralFriction=1.0)


        self.roboID = p.loadURDF(self.urdf_path, self.start_position, self.start_orientation, useFixedBase=False, flags=self.flags)

        # Identify Movable Joints
        self.numJoints = p.getNumJoints(self.roboID)
        self.movable_joints = []
        limits_low = []
        limits_high = []


        for joint in range(self.numJoints):
            joint_info = p.getJointInfo(self.roboID, joint)
            lower_limit, upper_limit = joint_info[8:10]
            # Identify revolute joints with limits
            if p.getJointInfo(self.roboID, joint)[2] in [0]:
                type = joint_info[12]
                type_str = type.decode("utf-8")
                if "continuous" in type_str:
                    limits_low.append(-1)
                    limits_high.append(1)
                else:
                    limits_low.append(lower_limit)
                    limits_high.append(upper_limit)

                self.movable_joints.append(joint)



        self.num_movable_joints = len(self.movable_joints)
        print(f"Number of Movable Joints: {self.num_movable_joints}")
        self.low_limits = np.array(limits_low)
        self.high_limits = np.array(limits_high)


        self.action_space = gym.spaces.Box(low=self.low_limits, high=self.high_limits, shape=(self.num_movable_joints,), dtype=np.float32)
        # print("\n _____ACTION SPACE_____ \n")
        # print("The Action Space is: ", self.action_space)

        # Define Observation Space (Joint Positions + Velocities + Base Position)
        """
        spaces.Box() defines the range of possible observations PPO receives at each time step:
        
            - self.num_movable_joints → Stores:
                -- Joint Positions (angle for each joint).
                -- Joint Velocities (velocity).
                -- +3 → Stores robot base position (X, Y, Z) to track movement.
                -- +4 → orientation quaternion 
                -- +6 → linear and angular velocities 
       
        """
        self.observation_space = gym.spaces.Box(low=-np.inf, high=np.inf, shape=(self.num_movable_joints * 2 + 13,), dtype=np.float32)
        # print("_____OBSERVATION SPACE_____ \n")
        # print("The State Space is: ", self.observation_space)

        self.stepCounter = 0  # Track steps per episode
        for i in range(p.getNumJoints(self.roboID)):
            joint_info = p.getJointInfo(self.roboID, i)
            link_name = joint_info[12].decode("utf-8")

            # Disable ALL collisions for links that are just visual joints
            if "L_joint_" in link_name or "Sphere_" in link_name or "B_joint" in link_name:
                link_index = joint_info[0]
                p.setCollisionFilterGroupMask(self.roboID, link_index, collisionFilterGroup=0, collisionFilterMask=0)

        self.last_place = []

    def step(self, action):
        """ Apply action to the robot and compute reward. """
        self.stepCounter += 1
        if self.render_mode:
            time.sleep(1.0 / 240.0)
        contacts = p.getContactPoints(bodyA=self.roboID, bodyB=self.terrainId)
        print("Number of contact points:", len(contacts))
        if len(contacts) == 0 and len(self.last_place) == 0:
            self.last_place, _ = p.getBasePositionAndOrientation(self.roboID)
        elif len(contacts) == 0 and len(self.last_place) != 0:
            self.position, _ = p.getBasePositionAndOrientation(self.roboID)
        elif len(contacts) != 0:
            self.last_place = []
            self.position = []
        # Apply actions to each movable joint
        for i, joint in enumerate(self.movable_joints):
            joint_info = p.getJointInfo(self.roboID, joint)
            type = joint_info[12]
            """ 
            p.setJointMotorControl2(self.robot, joint, p.POSITION_CONTROL, targetPosition=target_position)

                -> Moves the joint to target_position using position control.
                -> Other control modes (TORQUE_CONTROL, VELOCITY_CONTROL).
            """
            type_str = type.decode("utf-8")
            if "continuous" in type_str:
                p.setJointMotorControl2(self.roboID, joint, p.VELOCITY_CONTROL, force=0.000)
                p.setJointMotorControl2(self.roboID, joint, p.TORQUE_CONTROL, force=action[i] * self.f)
            else:
                p.setJointMotorControl2(self.roboID, joint, p.POSITION_CONTROL, targetPosition=action[i], targetVelocity=self.v, force=self.f) # normal speed is 2.0 radians/s and force is 10

        p.stepSimulation()
        robot_position, ori = p.getBasePositionAndOrientation(self.roboID)
        observation = self._get_observation(robot_position, ori)
        truncated = False
        # Compute reward
        reward, done, truncated = self.compute_reward(robot_position,contacts)

        return observation, reward, done, truncated, {}


    def _get_observation(self,robot_position,ori):
        try:
            lin_vel, ang_vel = p.getBaseVelocity(self.roboID)
        except Exception as e:
            print(f"[ERROR] getBaseVelocity failed: {e}")
            raise RuntimeError("Invalid robot: getBaseVelocity failed — aborting training and assigning fitness 0.0")

        # Get new state
        if self.num_movable_joints == 0:
            joint_states_position = np.zeros(3, dtype=np.float32)
            joint_states_velocity = np.zeros(3, dtype=np.float32)
        else:
            js = p.getJointStates(self.roboID, self.movable_joints)
            joint_states_position = np.array([s[0] for s in js], dtype=np.float32).reshape(-1)
            joint_states_velocity = np.array([s[1] for s in js], dtype=np.float32).reshape(-1)

        observation = np.hstack(
            [np.array(robot_position), np.array(ori), np.array(lin_vel), np.array(ang_vel), joint_states_position,
             joint_states_velocity]).astype(np.float32)
        # Garante que nunca é escalar:
        if observation.ndim == 0:
            observation = observation.reshape(1)

        return observation


    def compute_reward(self, current_position, contacts):
        distance_traveled = current_position[1] - self.start_position[1]
        # distance_traveled = np.linalg.norm(np.array(current_position) - self.start_position)
        reward = distance_traveled  # Reward moving forward, strong reward for distance travelled

        if self.plane == 0:
            # Terminate and punish if robot flies too high
            if current_position[2] > 0.3:  # adjust threshold depending on spawn height
                return -1.0, True, True  # strong punishment, end episode

            if current_position[2] < 0:
                return reward, False, True  # End episode
            # End episode after 20 seconds (4800 steps at 240Hz)
            done = self.stepCounter >= 4800
            return reward, done, False
        else:
            if not len(self.last_place) == 0:
                if (self.plane == 1 and (len(contacts) == 0) and (
                        current_position[2] - self.last_place[2] > 0.3 or current_position[2] - self.last_place[
                    2] < -0.3)):
                    return -1.0, True, True
            # End episode after 20 seconds (4800 steps at 240Hz)
            done = self.stepCounter >= 4800
            return reward, done, False

    def reset(self, seed = None, options = None):
        """ Reset the robot to a new starting position. """
        self.stepCounter = 0
        self.last_place = []
        p.resetSimulation()

        p.setAdditionalSearchPath(pybullet_data.getDataPath())
        p.setPhysicsEngineParameter(enableFileCaching=1)  # Avoid caching old URDFs
        # Show contact points in PyBullet
        p.setPhysicsEngineParameter(enableConeFriction=1)  # Improve friction
        p.setPhysicsEngineParameter(enableSAT=1)  # Use SAT solver for better collisions

        p.setGravity(0, 0, -9.8)
        if self.plane == 0:
            p.loadURDF("plane.urdf")
        else:
            heightData = np.loadtxt("../examples/terrain_data.csv", delimiter=',')
            terrainSize = 256  # Assuming the terrain is 256x256
            heightfieldData = heightData.flatten()  # Flatten to be applied on the PyBullet's function createCollisionShape

            # Create the terrain shape
            terrainShape = p.createCollisionShape(
                shapeType=p.GEOM_HEIGHTFIELD,
                meshScale=[2.8, 2.8, 40.0],  # Scale the terrain size and height
                heightfieldTextureScaling=terrainSize / 2,
                heightfieldData=heightfieldData,
                numHeightfieldRows=terrainSize,
                numHeightfieldColumns=terrainSize
            )

            # Create the terrain object
            terrainId = p.createMultiBody(0, terrainShape)
            p.resetBasePositionAndOrientation(terrainId, [0, 0, 8.5], [0, 0, 0, 1])  # Position
            p.changeVisualShape(terrainId, -1, rgbaColor=[1, 1, 1, 1])  # Color

            # Set the friction coefficient of the terrain
            p.changeDynamics(terrainId, -1, lateralFriction=1.0)

        self.roboID = p.loadURDF(self.urdf_path, self.start_position, self.start_orientation, useFixedBase=False, flags=self.flags)

        for i in range(p.getNumJoints(self.roboID)):
            joint_info = p.getJointInfo(self.roboID, i)
            link_name = joint_info[12].decode("utf-8")

            # Disable ALL collisions for links that are just visual joints
            if "L_joint_" in link_name or "Sphere_" in link_name or "B_joint" in link_name:
                link_index = joint_info[0]
                p.setCollisionFilterGroupMask(self.roboID, link_index, collisionFilterGroup=0, collisionFilterMask=0)

        self.let_robot_fall()
        # Return new observation
        observation = self._get_observation(self.start_position, self.start_orientation)
        try:
            # load robot, reset sim, etc.
            return observation, {}
        except Exception as e:
            print(f"[WARN] Env reset failed: {e}")
            # Mark as failed robot
            self.failed_robot = True
            self.episode_done = True
            return np.zeros(self.observation_space.shape, dtype=np.float32), {}

    def let_robot_fall(self, steps=500):
        """ Runs a few simulation steps to let the robot fall naturally. """
        for _ in range(steps):
            p.stepSimulation()
            #time.sleep(1.0 / 240.0)  # Small delay for real-time visualization

    def getRobotPosition(self):
        """ Returns the current robot position. """
        robot_position, _ = p.getBasePositionAndOrientation(self.roboID)
        return robot_position
    #
    # def close(self):
    #     """ Disconnect PyBullet. """
    #     p.disconnect()


# if __name__ == '__main__':
#     i = 0
#     ROBOT_URDF_PATH = f"/home/joaoraposo/Documents/GitHub/Evolutionary-Robotics-with-GE/corrected_robot{i}.urdf"  # ESTE É O ROBO
#     startOrientation = p.getQuaternionFromEuler([0, 0, 0])
#     startPos = [0, 0, 0.2]
#     flags = p.URDF_USE_SELF_COLLISION
#
#     env = URDFRobotEnv(ROBOT_URDF_PATH, startPos, startOrientation, flags, render=True)
