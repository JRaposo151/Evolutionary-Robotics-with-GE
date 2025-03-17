import math

import gym
from gym import spaces
import pybullet as p
import pybullet_data
import numpy as np
import time


class URDFRobotEnv(gym.Env):

    def __init__(self, urdf_path, render=False):
        super(URDFRobotEnv, self).__init__()
        self.urdf_path = urdf_path
        self.render_mode = render

        # Connect to PyBullet
        if self.render_mode:
            p.connect(p.GUI)
        else:
            p.connect(p.DIRECT)
        p.setAdditionalSearchPath(pybullet_data.getDataPath())

        roboID = p.loadURDF(urdf_path)
        """ Precisamos de saber quantos joints: """
        numJoints = p.getNumJoints(roboID)
        print(f"Number of joints here --> {numJoints}")


        # Define the action space.
        #
        self.action_space = spaces.Box(low=-1.0, high=1.0, shape=(numJoints,), dtype=np.float32)
        print("\n _____ACTION SPACE_____ \n")
        print("The Action Space is: ", self.action_space)


        # Define the observation space.
        # For instance, 6 joint positions and 6 joint velocities
        self.observation_space = spaces.Box(low=-np.inf, high=np.inf, shape=(12,), dtype=np.float32)
        print("_____OBSERVATION SPACE_____ \n")
        print("The State Space is: ", self.observation_space)


        self.robot = roboID

    def reset(self):
        p.resetSimulation()
        p.setGravity(0, 0, -9.8)
        # Optionally load a plane
        p.loadURDF("corrected_robot0.urdf")
        # Load your robot URDF; adjust base position as needed
        self.robot = p.loadURDF(self.urdf_path, basePosition=[0, 0, 0.5])

        # Wait a moment for the simulation to settle
        time.sleep(0.1)
        return self._get_observation()

    def step(self, action):
        # Apply the action to each joint (assuming you map each action component to a joint)
        num_joints = p.getNumJoints(self.robot)
        for joint in range(min(num_joints, len(action))):
            p.setJointMotorControl2(
                bodyIndex=self.robot,
                jointIndex=joint,
                controlMode=p.TORQUE_CONTROL,
                force=action[joint]
            )
        # Advance the simulation; you can step several times for a longer time step
        for _ in range(10):
            p.stepSimulation()
            time.sleep(1. / 240.)

        obs = self._get_observation()
        reward = self.reward()
        done = self._check_done()
        info = {}
        return obs, reward, done, info

    def get_observation(self):
        # For each joint, get position and velocity
        joint_states = p.getJointStates(self.robot, range(p.getNumJoints(self.robot)))
        positions = [state[0] for state in joint_states]
        velocities = [state[1] for state in joint_states]
        return np.array(positions + velocities, dtype=np.float32)

    def reward(self, basePosition, finalPosition):
        """EUCLIDIAN DISTANCE para calcular a distancia em linha reta do ponto de partida"""
        distance_traveled = math.sqrt((basePosition[0] - finalPosition[0]) ** 2 +
                                      (basePosition[1] - finalPosition[1]) ** 2 +
                                      (basePosition[2] - finalPosition[2]) ** 2)
        """DEFINIR UM REWARD TENDO EM CONTA A DISTANCIA PERCORRIDA, talvez uma percentagem, quando mais longe, recebe DIST / 100""" #TODO
        reward = distance_traveled / 100

        return reward

    def check_done(self):
        # Define a condition to end the episode. For example, if the robot falls or after a fixed time.
        """AQUI ESTAMOS A VER O QUAO OS ROBOS CONSEGUEM CHEGAR MAIS LONGE"""
        return False

    def render(self, mode='human'):
        pass


if __name__ == '__main__':
    i = 2
    a = URDFRobotEnv(f"/home/joaoraposo/Documents/GitHub/Evolutionary-Robotics-with-GE/corrected_robot{i}.urdf")

