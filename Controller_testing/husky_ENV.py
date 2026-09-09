import os
import time
from math import sqrt
import pandas as pd
import gymnasium as gym
import numpy as np
import pybullet as p
import pybullet_data
import torch
from stable_baselines3 import PPO
from stable_baselines3.common.vec_env import VecNormalize, SubprocVecEnv, DummyVecEnv
import matplotlib.pyplot as plt
from sge_FOR_ER.sge.sge import new_mart_terrain


class LaikagoEnv(gym.Env):
    metadata = {"render_modes": ["human"]}

    def __init__(self, path, plane, render=False, v=11.3, f=15.0):
        super().__init__()

        self.flags = p.URDF_USE_SELF_COLLISION
        self.path = path
        self.render_mode = render
        self.plane_mode = plane  # 0 = flat, 1 = mars
        self.v = v
        self.f = f

        self.counter = 0
        self.elapsed_steps = 0
        self.total_distance = 0.0
        self.previous_distance = 0.0
        self.samePlace_counter = 0
        self.last_place = []
        self.current_place = []

        self.alpha = 0.95
        self.filtered_ang_speed = np.zeros(3, dtype=np.float32)

        # connect once
        if self.render_mode:
            p.connect(p.GUI)
        else:
            p.connect(p.DIRECT)

        self._setup_world()
        self._load_robot()

        # action/obs spaces after robot is known
        self.num_joints = p.getNumJoints(self.robot)
        self.movable_joints = []
        for joint in range(self.num_joints):
            if p.getJointInfo(self.robot, joint)[2] == p.JOINT_REVOLUTE:
                self.movable_joints.append(joint)

        # if you really want only 4 actuated joints, keep first 4
        self.movable_joints = self.movable_joints[:4]
        self.num_movable_joints = len(self.movable_joints)

        self.action_space = gym.spaces.Box(
            low=-1.0,
            high=1.0,
            shape=(self.num_movable_joints,),
            dtype=np.float32,
        )

        obs_dim = 13 + 2 * self.num_movable_joints
        self.observation_space = gym.spaces.Box(
            low=-np.inf,
            high=np.inf,
            shape=(obs_dim,),
            dtype=np.float32,
        )

        # initial state trackers
        self.start_position = list(self.spawn_position)
        self.z_floor = self.spawn_position[2]
        self.y = self.spawn_position[1]

    def _setup_world(self):
        p.setAdditionalSearchPath(pybullet_data.getDataPath())
        p.setPhysicsEngineParameter(enableFileCaching=0)
        p.setPhysicsEngineParameter(enableConeFriction=1)
        p.setPhysicsEngineParameter(enableSAT=1)
        p.setPhysicsEngineParameter(numSubSteps=3)
        p.setGravity(0, 0, -9.8)

        if self.plane_mode == 0:
            self.terrain_body = p.loadURDF("plane.urdf")
            self.spawn_orientation = [0, 0, -0.7071, -0.7071]
            self.spawn_position = [0, 0, 0.5]
        else:
            self.terrain_body = new_mart_terrain.world_generation()
            p.changeDynamics(self.terrain_body, -1, lateralFriction=0.8)
            self.spawn_orientation = [0, 0, 0.7071, 0.7071]
            self.spawn_position = [65, 75, 10]

    def _load_robot(self):
        self.robot = p.loadURDF(
            self.path,
            self.spawn_position,
            self.spawn_orientation,
            useFixedBase=False,
            flags=self.flags,
        )
        self.let_robot_fall()

    def angular_speed_penalty(self, ang_vel):
        self.filtered_ang_speed = (
                (1 - self.alpha) * self.filtered_ang_speed
                + self.alpha * ang_vel)

        return np.linalg.norm(self.filtered_ang_speed)

    def _get_observation(self):
        pos, ori = p.getBasePositionAndOrientation(self.robot)
        lin_vel, ang_vel = p.getBaseVelocity(self.robot)

        if self.num_movable_joints == 0:
            joint_pos = np.zeros(0, dtype=np.float32)
            joint_vel = np.zeros(0, dtype=np.float32)
        else:
            joint_states = p.getJointStates(self.robot, self.movable_joints)
            joint_pos = np.array([s[0] for s in joint_states], dtype=np.float32)
            joint_vel = np.array([s[1] for s in joint_states], dtype=np.float32)

        obs = np.concatenate([
            np.array(pos, dtype=np.float32),
            np.array(ori, dtype=np.float32),
            np.array(lin_vel, dtype=np.float32),
            np.array(ang_vel, dtype=np.float32),
            joint_pos,
            joint_vel,
        ]).astype(np.float32)

        return obs

    def compute_reward(self, current_position, ang_vel, lin_vel):
        ang_speed_condition = self.angular_speed_penalty(np.array(ang_vel))
        reward_good_behaviour = self.start_position[1] - current_position[1]
        if ang_speed_condition < 0:
            reward = reward_good_behaviour + (-lin_vel[1] / 750) + ang_speed_condition / 1000 + (
                        current_position[2] - self.z_floor) * 2

        else:
            reward = reward_good_behaviour + (-lin_vel[1] / 750) - ang_speed_condition / 1000 + (
                        current_position[2] - self.z_floor) * 2



        self.z_floor = current_position[2]
        self.start_position[1] = current_position[1]

        # truncate if drifts too much in X
        if abs(self.start_position[0] - current_position[0]) > 2.0:
            self.total_distance = self.y - current_position[1]
            return -1.0, False, True

        done = self.counter >= 4800
        return reward, done, False

    def step(self, action):
        self.counter += 1
        self.elapsed_steps += 1

        if self.render_mode:
            time.sleep(1.0 / 480.0)

        contacts = p.getContactPoints(bodyA=self.robot, bodyB=self.terrain_body)
        if len(contacts) == 0 and len(self.last_place) == 0:
            self.last_place, _ = p.getBasePositionAndOrientation(self.robot)
        elif len(contacts) == 0 and len(self.last_place) != 0:
            self.position, _ = p.getBasePositionAndOrientation(self.robot)
        elif len(contacts) != 0:
            self.last_place = []
            self.position = []

        action = np.asarray(action, dtype=np.float32)

        for i, joint in enumerate(self.movable_joints):
            joint_info = p.getJointInfo(self.robot, joint)
            link_name = joint_info[12].decode("utf-8")


            p.setJointMotorControl2(
                    self.robot,
                    joint,
                    p.VELOCITY_CONTROL,
                    targetVelocity=float(action[i] * self.v),
                    force=float(self.f),
            )

        p.stepSimulation()

        robot_position, _ = p.getBasePositionAndOrientation(self.robot)
        lin_vel, ang_vel = p.getBaseVelocity(self.robot)

        obs = self._get_observation()
        reward, terminated, truncated = self.compute_reward(robot_position, ang_vel, lin_vel)

        self.total_distance = self.y - robot_position[1]

        info = {
            "total_distance": self.total_distance,
            "elapsed_steps": self.elapsed_steps,
        }

        return obs, reward, terminated, truncated, info

    def reset(self, seed=None, options=None):
        super().reset(seed=seed)

        self.counter = 0
        self.elapsed_steps = 0
        self.samePlace_counter = 0
        self.last_place = []
        self.current_place = []
        self.previous_distance = 0.0
        self.filtered_ang_speed = np.zeros(3, dtype=np.float32)

        p.resetSimulation()

        self._setup_world()
        self._load_robot()

        self.start_position = list(self.spawn_position)
        self.y = self.spawn_position[1]
        self.z_floor = self.spawn_position[2]
        self.total_distance = 0.0

        obs = self._get_observation()
        print(f"RESET HERE DONE : {self.total_distance}", flush=True)
        return obs, {}

    def let_robot_fall(self, steps=300):
        for _ in range(steps):
            p.stepSimulation()

    def get_robot_position(self):
        pos, _ = p.getBasePositionAndOrientation(self.robot)
        return pos

    def close(self):
        p.disconnect()
def make_husky_env(robot_path, plane, render=False):
    def _init():
        env = LaikagoEnv(robot_path, plane, render=render)
        return env
    return _init


def torque():
    seed = 10
    path = os.path.join(pybullet_data.getDataPath(), "husky/husky.urdf")

    """
    ATIVAÇÃO DE CUDA AQUI 
    """
    torch.device('cuda:'+str(torch.cuda.device_count()) if torch.cuda.is_available() else 'cpu')
    print('Using device:', 'cuda' if torch.cuda.is_available() else 'cpu', ', device number:',
          torch.cuda.device_count(), ', GPUs in system:', torch.cuda.device_count())

# ::::::::::::::: Train the PPO model on this environment ::::::::::::::::::::::
    if not os.path.exists(f"models_PPO_Test_NEW_REWARD/ppo_husky_horizontal_velo_updatePosition.zip"):
        # Train the PPO model on this environment


        # Number of environments you want to train in parallel
        n_envs = 1
        plane = 0
        # Create multiple environments using your factory
        env_fns = [make_husky_env(path, plane, render=False) for _ in range(n_envs)]
        vec_env = DummyVecEnv(env_fns)  # Or use DummyVecEnv if you have debugging needs
        env = VecNormalize(vec_env, training=True, norm_obs=True, norm_reward=True, clip_obs=10.0)
        model = PPO(policy='MlpPolicy',
                            env=env,
                            learning_rate=0.0003,
                            n_steps=2048,
                            batch_size=64,
                            n_epochs=10,
                            gamma=0.99,
                            gae_lambda=0.95,
                            verbose=1,
                            seed=seed,
                            )
        model.learn(total_timesteps=300000)
        # Save the trained model
        if plane == 0:
            model.save(f"models_PPO_Test_NEW_REWARD/ppo_husky_horizontal_velo_updatePosition")
            print(f"CAR Trained")
            env.save("models_PPO_Test_NEW_REWARD/ppo_husky_horizontal_velo_updatePosition.pkl")

        elif plane == 1:
            model.save(f"models_PPO_Test_NEW_REWARD/ppo_husky_Marte_4800_velo_updatePosition")
            print(f"CAR Trained")
            env.save("models_PPO_Test_NEW_REWARD/ppo_husky_Marte_4800_velo_updatePosition.pkl")
        env.close()
# ::::::::::::::: Train the PPO model on this environment ::::::::::::::::::::::



# --------------------- Testing/Visualization Phase ------------------------
    with open("Results3.txt", "w") as file:
        plane = 1
        test_env = [make_husky_env(path, plane, render=True) for _ in range(1)]
        test_env = DummyVecEnv(test_env)  # Or use DummyVecEnv if you have debugging needs
        if plane == 0:
            test_env = VecNormalize.load("models_PPO_Test_NEW_REWARD/ppo_husky_horizontal_velo_updatePosition.pkl", test_env)
            model = PPO.load(f"models_PPO_Test_NEW_REWARD/ppo_husky_horizontal_velo_updatePosition", env=test_env)

        if plane == 1:
            test_env = VecNormalize.load("models_PPO_Test_NEW_REWARD/ppo_husky_Marte_4800_velo_updatePosition.pkl", test_env)
            model = PPO.load(f"models_PPO_Test_NEW_REWARD/ppo_husky_Marte_4800_velo_updatePosition", env=test_env)

        #  do not update them at test time
        test_env.training = False
        # reward normalization is not needed at test time
        test_env.norm_reward = False
        # Testing loop: run several episodes and record rewards
        episode_rewards = []
        episode_distances = []
        max_episode_distances = []
        episode_times = []
        raw_env = test_env.envs[0]

        num_episodes = 0
        # Run a fixed number of simulation steps

        obs = test_env.reset()
        for ep in range(30):
            terminated = False
            max_distance = 0.0
            robot_pos = raw_env.get_robot_position()
            p.resetDebugVisualizerCamera(cameraDistance=0.5,
                                         cameraYaw=50,
                                         cameraPitch=-10,
                                         cameraTargetPosition=robot_pos)
            while not terminated:
                robot_pos = raw_env.get_robot_position()
                p.resetDebugVisualizerCamera(cameraDistance=5,
                                             cameraYaw=50,
                                             cameraPitch=-30,
                                             cameraTargetPosition=robot_pos)
                action, _ = model.predict(obs, deterministic=False)
                obs, reward, terminated, infos = test_env.step(action)

                # --- safe unpacking for VecEnv (works if returns arrays / tuples) ---
                # reward may be array-like (shape (n_envs,)) or scalar
                if isinstance(reward, (list, tuple, np.ndarray)):
                    r = float(reward[0])
                else:
                    r = float(reward)

                # terminated may be array-like too
                if isinstance(terminated, (list, tuple, np.ndarray)):
                    term = bool(terminated[0])
                else:
                    term = bool(terminated)

                # infos can be a list of dicts (for VecEnv) or dict
                if isinstance(infos, (list, tuple)):
                    info = infos[0] if len(infos) > 0 else {}
                else:
                    info = infos if isinstance(infos, dict) else {}

                # keep final step reward (overwrite each step)
                final_reward = r
                terminated = term
                elapsed_steps = info.get("elapsed_steps", 0)
                if max_distance < info.get("total_distance", 0.0):
                    max_distance = info.get("total_distance", 0.0)
                #if ep == 9 and elapsed_steps >= 4400:
                    #print(max_distance, elapsed_steps)
            # Episode ended
            total_distance = info.get("total_distance", 0.0)
            elapsed_steps = info.get("elapsed_steps", 0)

            print(f"Episode {ep + 1} final distance: {total_distance:.2f}")



            max_episode_distances.append(max_distance)
            episode_rewards.append(final_reward)  # final reward (not sum)
            episode_distances.append(total_distance)
            episode_times.append(elapsed_steps)

            num_episodes += 1
            obs = test_env.reset()  # reset once per episode

        # --- compute summary safely ---
        if episode_rewards:
            avg_reward = float(np.mean(episode_rewards))
            std_reward = float(np.std(episode_rewards))
            avg_distance = float(np.mean(episode_distances)) if episode_distances else 0.0
            std_distance = float(np.std(episode_distances)) if episode_distances else 0.0
            mean_len = float(np.mean(episode_times)) if episode_times else 0.0
            std_len = float(np.std(episode_times)) if episode_times else 0.0
        else:
            avg_reward = std_reward = avg_distance = std_distance = mean_len = std_len = 0.0

        avg_max_distance = float(np.mean(max_episode_distances)) if max_episode_distances else 0.0
        std_max_distance = float(np.std(max_episode_distances)) if max_episode_distances else 0.0



        print("\n=== Evaluation Results ===")
        print(f"Total Episodes: {num_episodes}")
        print(f"Average Reward: {avg_reward:.2f}")
        print(f"Standard Deviation: {std_reward:.2f}")
        print(f"Average Distance: {avg_distance:.2f} ± {std_distance:.2f}")
        print(f"Average Time (steps): {mean_len:.1f} ± {std_len:.1f}")
        print(f"Average Max Distance: {avg_max_distance:.2f} ± {std_max_distance:.2f}")

        # Save per-episode results
        results_df = pd.DataFrame({
            "Episode": np.arange(1, len(episode_rewards) + 1),
            "Reward": episode_rewards,
            "Distance": episode_distances,
            "MaxDistance": max_episode_distances,
            "Steps": episode_times
        })

        results_df.to_csv("Husky_like_robot&controllers.csv", index=False)

        plt.figure(figsize=(10, 5))
        plt.plot(range(1, len(episode_rewards) + 1), episode_rewards, marker="o", label="Episode Reward")
        plt.axhline(avg_reward, color="g", linestyle="--", label=f"Avg Reward ({avg_reward:.2f})")
        plt.fill_between(range(1, len(episode_rewards) + 1),
                         avg_reward - std_reward,
                         avg_reward + std_reward,
                         color="g", alpha=0.2, label="±1 Std Dev")
        plt.title("Episode Rewards")
        plt.xlabel("Episode")
        plt.ylabel("Reward")
        plt.legend()
        plt.grid(True, linestyle=":", alpha=0.7)
        plt.tight_layout()
        plt.show()

        # --- plotting (guard against empty lists) ---
        if episode_distances:
            x = np.arange(len(episode_distances))

            plt.figure(figsize=(10, 5))
            plt.plot(x, episode_distances, marker='o', label="Last distance")
            plt.plot(x, max_episode_distances, color='red', marker='*',
                     linestyle='-', linewidth=1.2, markersize=10, label="Max distance (within episode)")

            best_so_far = np.maximum.accumulate(max_episode_distances)

            plt.axhline(avg_distance, color='b', linestyle='--', label=f"Avg Distance ({avg_distance:.2f})")
            plt.axhline(avg_max_distance, color="r", linestyle='--', label=f"Avg Max Dist ({avg_max_distance:.2f})")

            plt.title("Episode Distances")
            plt.xlabel("Episode")
            plt.ylabel("Distance")
            plt.legend()
            plt.grid(True)
            plt.tight_layout()
            plt.show()

        if episode_times:
            plt.figure(figsize=(8, 4))
            plt.bar(range(1, len(episode_times) + 1), episode_times)
            plt.axhline(mean_len, color='r', linestyle='--', label=f"Mean ({mean_len:.1f})")
            plt.title("Episode Lengths (Survival Time)")
            plt.xlabel("Episode")
            plt.ylabel("Steps until Termination")
            plt.legend()
            plt.grid(True, linestyle=':', alpha=0.6)
            plt.tight_layout()
            plt.show()


        test_env.close()

if __name__ == "__main__":
    torque()