import os
import time
import gymnasium as gym
import numpy as np
import pybullet as p
import pybullet_data
import torch
from stable_baselines3 import PPO

class LaikagoEnv(gym.Env):
    def __init__(self,
                 path,
                 render=True):

        super(LaikagoEnv, self).__init__()
        self.flags = p.URDF_USE_SELF_COLLISION
        self.path = path
        self.counter = 0
        # Observation: base position (3), orientation quaternion (4),
        # linear velocity (3), angular velocity (3), joint positions (4) = 17 dimensions.
        self.observation_space = gym.spaces.Box(low=-np.inf, high=np.inf, shape=(17,), dtype=np.float32)
        self.action_space = gym.spaces.Box(low=-1, high=1, shape=(4,), dtype=np.float32)  # 4 joints
        self.render_mode = render

        # Connect to PyBullet only if not already connected.
        if self.render_mode:
            p.connect(p.GUI)
            # Optionally, enable real-time simulation for smoother rendering.                p.setRealTimeSimulation(1)
        else:
            p.connect(p.DIRECT)

        p.setAdditionalSearchPath(pybullet_data.getDataPath())
        p.setPhysicsEngineParameter(enableFileCaching=0)  # Avoid caching old URDFs
        # Show contact points in PyBullet
        p.setPhysicsEngineParameter(enableConeFriction=1)  # Improve friction
        p.setPhysicsEngineParameter(enableSAT=1)  # Use SAT solver for better collisions

        p.setGravity(0, 0, -9.8)
        p.loadURDF("plane.urdf")
        useFixedBase = False

        self.ori = [0, 0, 0.1, 0]
        self.pos = [0, 0, 0]

        self.robot = p.loadURDF(self.path, [0, 0, 0.1], self.ori, useFixedBase=useFixedBase, flags=self.flags)
        self.let_robot_fall()

        # Identify Movable Joints
        self.numJoints = p.getNumJoints(self.robot)
        self.movable_joints = []

        for joint in range(self.numJoints):
            # Identify revolute joints with limits
            if p.getJointInfo(self.robot, joint)[2] in [0]:
                self.movable_joints.append(joint)

        self.num_movable_joints = len(self.movable_joints)
        # print(f"Number of Movable Joints: {self.num_movable_joints}")



    def step(self, action):
        if self.render_mode:
            time.sleep(1.0 / 240.0)
        new_action = 20 * action
        #print(new_action)
        self.counter += 1
        for joint in self.movable_joints:
            p.setJointMotorControl2(self.robot, joint, p.VELOCITY_CONTROL, force=0.000)

        for i, joint in enumerate(self.movable_joints):
            p.setJointMotorControl2(self.robot, joint, p.TORQUE_CONTROL, force=new_action[i])
        p.stepSimulation()
        #time.sleep(1.0 / 240.0)

        obs = self._get_observation()
        # Get position and orientation
        pos, _ = p.getBasePositionAndOrientation(self.robot)
        # Set the camera to follow the robot
        p.resetDebugVisualizerCamera(
            cameraDistance=2.5,  # Distance from robot
            cameraYaw=50,  # Horizontal angle
            cameraPitch=-35,  # Vertical angle
            cameraTargetPosition=pos  # Where the camera looks at
        )
        # Reward function: encourage forward motion, penalize instability
        distance_traveled = pos[0] - self.pos[0]
        self.pos = pos

        reward = distance_traveled  # Encourage forward motion
        print("Reward:",reward)
        # Check if robot has fallen

        terminated = False
        truncated = False
        # Penalize falling
        if self.counter == 4800 or self.pos[2] < -0.1:
            self.counter = 0
            terminated = True
        return obs, reward, terminated, truncated, {}

    def reset(self, **kwargs):
        p.resetSimulation()
        p.setGravity(0, 0, -9.8)
        p.loadURDF("plane.urdf")
        useFixedBase = False
        self.robot = p.loadURDF(self.path, [0, 0, 0.1], self.ori, useFixedBase=useFixedBase, flags=self.flags)
        self.let_robot_fall()

        obs = self._get_observation()

        return obs, {}

    def _get_observation(self):
        # Get base position and orientation (quaternion)
        pos, ori = p.getBasePositionAndOrientation(self.robot)
        # Get linear and angular velocities of the base
        lin_vel, ang_vel = p.getBaseVelocity(self.robot)
        # Get joint positions for all 12 actuated joints
        joint_states = [p.getJointState(self.robot, i)[0] for i in range(4)]
        # Use np.hstack to flatten and combine all components into a single 1D array
        obs = np.hstack([np.array(pos), np.array(ori), np.array(lin_vel), np.array(ang_vel), np.array(joint_states)])
        return obs.astype(np.float32)



    def let_robot_fall(self, steps=300):
        """ Runs a few simulation steps to let the robot fall naturally. """
        for _ in range(steps):
            p.stepSimulation()


    def render(self, mode='human'):
        pass

    def close(self):
        p.resetSimulation()
        p.disconnect()

def make_husky_env(robot_path, render=False):
    def _init():
        env = LaikagoEnv(path=robot_path, render=render)
        return env
    return _init


def torque():
    seed = 10
    path = "husky/husky.urdf"


    """
    ATIVAÇÃO DE CUDA AQUI 
    """
    torch.device('cuda:'+str(torch.cuda.device_count()) if torch.cuda.is_available() else 'cpu')
    print('Using device:', 'cuda' if torch.cuda.is_available() else 'cpu', ', device number:',
          torch.cuda.device_count(), ', GPUs in system:', torch.cuda.device_count())

# ::::::::::::::: Train the PPO model on this environment ::::::::::::::::::::::
    if not os.path.exists(f"ppo_husky_TORQUE_CONTROL.zip"):
        # Train the PPO model on this environment
        from stable_baselines3.common.vec_env import SubprocVecEnv

        # Number of environments you want to train in parallel
        n_envs = 4

        # Create multiple environments using your factory
        env_fns = [make_husky_env(path, render=True) for _ in range(n_envs)]
        vec_env = SubprocVecEnv(env_fns)  # Or use DummyVecEnv if you have debugging needs
        model = PPO(policy='MlpPolicy',
                            env=vec_env,
                            learning_rate=3e-4,
                            n_steps=2048,
                            batch_size=64,
                            n_epochs=4,
                            gamma=0.999,
                            gae_lambda=0.98,
                            ent_coef=0.01,
                            verbose=1,
                            seed=seed,
                            tensorboard_log="./logs_1/"
                            )
        model.learn(total_timesteps=300000)
        # Save the trained model
        model.save(f"ppo_husky_TORQUE_CONTROL")
        print(f"CAR Trained")
        vec_env.close()
# ::::::::::::::: Train the PPO model on this environment ::::::::::::::::::::::



# --------------------- Testing/Visualization Phase ------------------------
    with open("Results3.txt", "w") as file:
        model = PPO.load(f"ppo_husky_TORQUE_CONTROL")
        test_env = LaikagoEnv(path, render=True)

        # Testing loop: run several episodes and record rewards
        episode_rewards = []
        total_reward = 0
        num_episodes = 0
        obs, _ = test_env.reset()
        # Run a fixed number of simulation steps

        for _ in range(4800):
            action, _ = model.predict(obs, deterministic=False)
            obs, reward, terminated, truncated, _ = test_env.step(action)
            total_reward += reward
            if terminated or truncated:
                episode_rewards.append(reward)
                num_episodes += 1
                print(f"Episode {num_episodes} reward: {reward:.2f}")
                obs, _ = test_env.reset()
                break


        test_env.close()

        # Compute and save statistics
        robot_name = f"ppo_husky_TORQUE_CONTROL"
        if episode_rewards:
            mean_reward = np.mean(episode_rewards)
            std_reward = np.std(episode_rewards)
            print("Mean reward:", total_reward)
            #print("Std reward:", std_reward)

            # Write results to file
            #file.write(
                #f"{robot_name}, Mean Reward: {mean_reward:.2f}, Std Reward: {std_reward:.2f}\n")
        else:
            print("No episodes completed.")
            file.write(f"{robot_name}, No episodes completed.\n")
