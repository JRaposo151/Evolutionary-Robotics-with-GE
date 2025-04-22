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
                 render=False):

        super(LaikagoEnv, self).__init__()
        self.flags = p.URDF_USE_SELF_COLLISION
        self.path = path

        # Observation: base position (3), orientation quaternion (4),
        # linear velocity (3), angular velocity (3), joint positions (12) = 25 dimensions.
        self.observation_space = gym.spaces.Box(low=-np.inf, high=np.inf, shape=(25,), dtype=np.float32)
        self.action_space = gym.spaces.Box(low=-1, high=1, shape=(12,), dtype=np.float32)  # 12 joints
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

        self.ori = [0, 0.5, 0.5, 0]
        self.pos = [0, 0, 0]

        self.robot = p.loadURDF(self.path, [0, 0, 0.5], self.ori, useFixedBase=useFixedBase, flags=self.flags)
        self.let_robot_fall()

        # Identify Movable Joints
        self.numJoints = p.getNumJoints(self.robot)
        self.movable_joints = []

        for joint in range(self.numJoints):
            joint_info = p.getJointInfo(self.robot, joint)

            # Identify revolute joints with limits
            if p.getJointInfo(self.robot, joint)[2] in [0]:
                self.movable_joints.append(joint)

        self.num_movable_joints = len(self.movable_joints)
        # print(f"Number of Movable Joints: {self.num_movable_joints}")

        self.counter = 0

    def step(self, action):
        self.counter += 1
        if self.render_mode:
            time.sleep(1.0 / 240.0)
        # print(f"ACTION: {action}" )
        action_new = 100 * action

        for joint in self.movable_joints:
            p.setJointMotorControl2(self.robot, joint, p.VELOCITY_CONTROL, force=0.000)

        for i, joint in enumerate(self.movable_joints):
            p.setJointMotorControl2(self.robot, joint, p.TORQUE_CONTROL, force=action_new[i])
        p.stepSimulation()

        obs = self._get_observation()
        # Get position and orientation
        pos, _ = p.getBasePositionAndOrientation(self.robot)
        # Reward function: encourage forward motion, penalize instability
        distance_traveled = pos[1] - self.pos[1]
        self.pos = pos

        reward = distance_traveled  # Encourage forward motion
        #print("Reward:", reward)
        # Check if robot has fallen

        terminated = False
        truncated = False
        # Penalize falling
        if self.counter == 4800 or pos[2] < 0.25:  # Adjust threshold if needed:
            self.counter = 0
            terminated = True
        return obs, reward, terminated, truncated, {}

    def reset(self, **kwargs):
        p.resetSimulation()
        p.setGravity(0, 0, -9.8)
        p.loadURDF("plane.urdf")
        useFixedBase = False
        self.robot = p.loadURDF(self.path, [0, 0, 0.5], self.ori, useFixedBase=useFixedBase, flags=self.flags)
        self.let_robot_fall()

        obs = self._get_observation()

        return obs, {}

    def _get_observation(self):
        # Get base position and orientation (quaternion)
        pos, ori = p.getBasePositionAndOrientation(self.robot)
        # Get linear and angular velocities of the base
        lin_vel, ang_vel = p.getBaseVelocity(self.robot)
        # Get joint positions for all 12 actuated joints
        joint_states = [p.getJointState(self.robot, i)[0] for i in range(12)]
        # Use np.hstack to flatten and combine all components into a single 1D array
        obs = np.hstack([np.array(pos), np.array(ori), np.array(lin_vel), np.array(ang_vel), np.array(joint_states)])
        return obs.astype(np.float32)



    def let_robot_fall(self, steps=300):
        """ Runs a few simulation steps to let the robot fall naturally. """
        for _ in range(steps):
            p.stepSimulation()
            time.sleep(1.0 / 240.0)  # Small delay for real-time visualization


    def render(self, mode='human'):
        pass

    def close(self):
        p.resetSimulation()
        p.disconnect()


def make_laikago_env(robot_path, render=False):
    def _init():
        env = LaikagoEnv(path=robot_path, render=render)
        return env
    return _init


def velocity():
    seed = 10
    path = "laikago/laikago_toes.urdf"


    """
    ATIVAÇÃO DE CUDA AQUI 
    """
    torch.device('cuda:'+str(torch.cuda.device_count()) if torch.cuda.is_available() else 'cpu')
    print('Using device:', 'cuda' if torch.cuda.is_available() else 'cpu', ', device number:',
          torch.cuda.device_count(), ', GPUs in system:', torch.cuda.device_count())
    print("PyTorch CUDA version:", torch.version.cuda)

    # ::::::::::::::: Train the PPO model on this environment ::::::::::::::::::::::

    if not os.path.exists(f"ppo_laikago_TORQUE_CONTROL_0.zip"):
        # Train the PPO model on this environment
        from stable_baselines3.common.vec_env import SubprocVecEnv

        # Number of environments you want to train in parallel
        # n_envs = 1
        #
        # # Create multiple environments using your factory
        # env_fns = [make_laikago_env(path, render=False) for _ in range(n_envs)]
        # vec_env = SubprocVecEnv(env_fns)  # Or use DummyVecEnv if you have debugging needs
        env = LaikagoEnv(path, render=False)
        model = PPO(policy='MlpPolicy',
                            env=env,
                            learning_rate=2e-5,
                            n_steps=2048,
                            batch_size=2048,
                            n_epochs=5,
                            gamma=0.95,   # PODEREI DIMUNUIR PARA  a smaller gamma (e.g., 0.98) makes the agent focus slightly more on immediate rewards, which can lead to trying more diverse behaviors early on.
                            gae_lambda=0.98,
                            ent_coef=1e-3,  # Increase Entropy Regularization This term encourages exploration by penalizing certainty (i.e., encourages the policy to remain more "random").
                            verbose=1,
                            seed=seed,
                            # use_sde=True, #gSDE introduces structured noise that depends on the state, improving exploration in high-dimensional or continuous action spaces.
                            # sde_sample_freq=2048,  # how often to resample noise; 4 = every 4 steps
                            tensorboard_log="./logs_1/"
                            )
        model.learn(total_timesteps=300000)
        # Save the trained model
        model.save(f"ppo_laikago_TORQUE_CONTROL_0")
        print(f" DOG Trained")
        env.close()
# ::::::::::::::: Train the PPO model on this environment ::::::::::::::::::::::



# --------------------- Testing/Visualization Phase ------------------------
    with open("Results2.txt", "w") as file:

        model = PPO.load(f"ppo_laikago_TORQUE_CONTROL_0")
        test_env = LaikagoEnv(path, render=True)

        # Testing loop: run several episodes and record rewards
        episode_rewards = []
        num_episodes = 0
        obs, _ = test_env.reset()

        # Run a fixed number of simulation steps
        for _ in range(4800):
            action, _ = model.predict(obs, deterministic=False)
            obs, reward, terminated, truncated, _ = test_env.step(action)

            if terminated or truncated:
                episode_rewards.append(reward)
                num_episodes += 1
                print(f"Episode {num_episodes} reward: {reward}")
                obs, _ = test_env.reset()


        test_env.close()

        # Compute and save statistics
        robot_name = f"ppo_laikago_VELOCITY_CONTROL"
        if episode_rewards:
            mean_reward = np.mean(episode_rewards)
            std_reward = np.std(episode_rewards)
            print("Mean reward:", mean_reward)
            print("Std reward:", std_reward)

            # Write results to file
            file.write(
                        f"{robot_name}, Mean Reward: {mean_reward:.2f}, Std Reward: {std_reward:.2f}\n")
        else:
            print("No episodes completed.")
            file.write(f"{robot_name}, No episodes completed.\n")

