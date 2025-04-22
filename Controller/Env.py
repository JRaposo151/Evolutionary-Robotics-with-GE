import os
import time
import pybullet as p
import pybullet_data
import numpy as np
import gym  # note the change here
from gym import spaces



class URDFRobotEnv(gym.Env):
    def __init__(self,
                 urdf_path,
                 startPos,
                 startOrientation,
                 flags,
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

        self.urdf_path = urdf_path
        self.render_mode = render
        self.start_position = np.array(startPos)  # Store starting position TODO CORRIGIR AQUI PARA DEPOIS A DISTANCIA SE BEM CALCULADA
        self.start_orientation = np.array(startOrientation)
        #self.f = f
        #self.v = v

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
        p.loadURDF("plane.urdf")

        if not os.path.exists(urdf_path):
            raise FileNotFoundError(f"ERROR: URDF file not found: {urdf_path}")

        self.roboID = p.loadURDF(urdf_path, self.start_position, startOrientation, useFixedBase=False, flags=flags)

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
                self.movable_joints.append(joint)
                limits_low.append(lower_limit)
                limits_high.append(upper_limit)


        self.num_movable_joints = len(self.movable_joints)
        print(f"Number of Movable Joints: {self.num_movable_joints}")
        self.low_limits = np.array(limits_low)
        self.high_limits = np.array(limits_high)


        self.action_space = spaces.Box(low=self.low_limits, high=self.high_limits, shape=(self.num_movable_joints,), dtype=np.float32)
        print("\n _____ACTION SPACE_____ \n")
        print("The Action Space is: ", self.action_space)

        # Define Observation Space (Joint Positions + Velocities + Base Position)
        """
        spaces.Box() defines the range of possible observations PPO receives at each time step:
        
            - self.num_movable_joints → Number of controllable joints.
            - self.num_movable_joints → Stores:
                -- Joint Positions (angle for each joint).
                -- +3 → Stores robot base position (X, Y, Z) to track movement.
        """
        self.observation_space = spaces.Box(low=-np.inf, high=np.inf, shape=(self.num_movable_joints + 3,), dtype=np.float32)
        print("_____OBSERVATION SPACE_____ \n")
        print("The State Space is: ", self.observation_space)

        self.stepCounter = 0  # Track steps per episode

    def step(self, action):
        """ Apply action to the robot and compute reward. """
        self.stepCounter += 1

        # Apply actions to each movable joint
        for i, joint in enumerate(self.movable_joints):

            """
            target_position = np.clip(action[i], self.low_limits[i], self.high_limits[i])

                -> Ensures PPO’s output doesn't exceed the allowed joint range.
                -> Example: If a revolute joint can move between -0.75 and 0.75 radians, this clips the action to stay in that range.
                
                
            p.setJointMotorControl2(self.robot, joint, p.POSITION_CONTROL, targetPosition=target_position)

                -> Moves the joint to target_position using position control.
                -> Other control modes (TORQUE_CONTROL, VELOCITY_CONTROL).
            """
            target_position = np.clip(action[i], self.low_limits[i], self.high_limits[i])

            p.setJointMotorControl2(self.roboID, joint, p.POSITION_CONTROL, targetPosition=target_position, targetVelocity=2, force=10) # normal speed is 2.0 radians/s and force is 10

        p.stepSimulation()

        # Get new state
        joint_positions = []
        joint_velocities = []
        for joint in self.movable_joints:
            state = p.getJointState(self.roboID, joint)
            joint_positions.append(state[0])  # Joint position
            joint_velocities.append(state[1])  # Joint velocity

        robot_position, _ = p.getBasePositionAndOrientation(self.roboID)
        observation = np.array(joint_positions + list(robot_position))
        truncated = False

        # Compute reward
        reward, done, truncated = self.compute_reward(robot_position)

        return observation, reward, done, truncated, {}

    def compute_reward(self, current_position):
        reward = 0
        """ Reward function based on Euclidean distance traveled.

            The reward function helps PPO learn how to make the robot move forward.
            It calculates how far the robot has traveled from its start position using Euclidean distance.

            Step-by-Step Breakdown:
                - Compute the Euclidean distance from the start position ( https://numpy.org/doc/2.1/reference/generated/numpy.linalg.norm.html ):
                    -> distance_traveled = np.linalg.norm(np.array(current_position) - self.start_position)

                - np.linalg.norm() calculates the straight-line distance between:
                    -> current_position → Robot’s current (X, Y, Z) location.
                    -> self.start_position → Robot’s spawn location.

            Give higher rewards for greater distances:
                -> reward = distance_traveled * 10

            The further the robot moves, the higher the reward.
            This encourages fast and efficient movement.


            Same as:

            EUCLIDIAN DISTANCE para calcular a distancia em linha reta do ponto de partida:
                distance_traveled = math.sqrt((cubePos[0] - startPos[0])**2 +
                                              (cubePos[1] - startPos[1])**2 +
                                              (cubePos[2] - startPos[2])**2)

        """
        distance_traveled = np.linalg.norm(np.array(current_position) - self.start_position)

        if distance_traveled >= 0:
            reward = distance_traveled  # Reward moving forward, strong reward for distance travelled

        if current_position[2] < 0:
            reward -= 1000
            return reward, False, True   # End episode

        # End episode after 20 seconds (4800 steps at 240Hz)
        done = self.stepCounter >= 4800

        return reward, done, False

    def reset(self, seed = None, options = None):
        """ Reset the robot to a new starting position. """
        self.stepCounter = 0

        p.resetBasePositionAndOrientation(self.roboID, self.start_position, self.start_orientation)

        # Reset all movable joints
        for joint in self.movable_joints:
            p.resetJointState(self.roboID, joint, targetValue=0, targetVelocity=0)

        #TODO SE CALHAR METER O ROBO A CAIR PRIMEIRO APOS O RESET

        # Return new observation
        joint_positions = [0] * self.num_movable_joints
        observation = np.array(joint_positions + list(self.start_position))

        info = {}
        return observation, info

    def getRobotPosition(self):
        robot_position, _ = p.getBasePositionAndOrientation(self.roboID)
        return robot_position

    def let_robot_fall(self, steps=500):
        """ Runs a few simulation steps to let the robot fall naturally. """
        for _ in range(steps):
            p.stepSimulation()
            time.sleep(1.0 / 240.0)  # Small delay for real-time visualization

    def close(self):
        """ Disconnect PyBullet. """
        p.disconnect()


# if __name__ == '__main__':
#     i = 0
#     ROBOT_URDF_PATH = f"/home/joaoraposo/Documents/GitHub/Evolutionary-Robotics-with-GE/corrected_robot{i}.urdf"  # ESTE É O ROBO
#     startOrientation = p.getQuaternionFromEuler([0, 0, 0])
#     startPos = [0, 0, 0.2]
#     flags = p.URDF_USE_SELF_COLLISION
#
#     env = URDFRobotEnv(ROBOT_URDF_PATH, startPos, startOrientation, flags, render=True)
