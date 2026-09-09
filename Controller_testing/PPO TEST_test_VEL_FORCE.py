import os
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
from stable_baselines3 import PPO
from sge_FOR_ER.sge.sge.Env_mars import URDFRobotEnv
import pybullet as p
import random
import torch

from stable_baselines3.common.vec_env import VecNormalize, DummyVecEnv
"""
:::::::::::::::::: EVALUATE THE ROBOT AND ITS CONTROLLER :::::::::::::::::: 
"""
# Ensure results directory exists
results_dir = "Husky_like_robot&controllers"
os.makedirs(results_dir, exist_ok=True)
seed = 44
random.seed(seed)
np.random.seed(seed)
torch.manual_seed(seed)
forces = [15] #15
velocities = ["30"] #67


def URDFRobotEnv_make(ROBOT_URDF_PATH, velocity, force, render):
    def _init():
        env = URDFRobotEnv(ROBOT_URDF_PATH, velocity, force, render=render)
        return env
    return _init

# Open the file for writing evaluation results
with open(os.path.join(results_dir, "evaluation_results_TESTES_velocidade_Força.txt"), 'w') as f:
    name = 0
    f.write("Evaluation Results:\n\n")
    # Run evaluation for robots
    for force in forces:
        # turn 0.05 → "0_05", 0.1 → "0_1", 1.0 → "1_0" (or "1" if you prefer)
        force_str = str(force).rstrip('0').rstrip('.')  # e.g. "0.05"→"0.05"; "1.0"→"1"
        force_str = force_str.replace('.', '_')  # e.g. "0.05"→"0_05"

        for velocity in velocities:

            print("------------- ------------- ------------- ------------- ")
            print(f"------------- Evaluating Robot number {name} Force {force}  Velocity {velocity} -------------")
            print("------------- ------------- ------------- ------------- ")


            vec_path_2 = f"/home/joaoraposo/Desktop/Resultados_ANYDESK/__50cross_5mut/mars_S_42/robots_ind/best_gen_0" + velocity + ".pkl"
            ROBOT_URDF_PATH = f"/home/joaoraposo/Desktop/Resultados_ANYDESK/__50cross_5mut/mars_S_42/robots_ind/best_gen_0" + velocity + ".urdf"
            model_name = f"/home/joaoraposo/Desktop/Resultados_ANYDESK/__50cross_5mut/mars_S_42/robots_ind/best_gen_0" + velocity


            # # Ensure the model file exists
            if not os.path.exists(ROBOT_URDF_PATH):
                print(f"Model {model_name} not found. Skipping...")
                continue
            env = DummyVecEnv([URDFRobotEnv_make(ROBOT_URDF_PATH, velocity=67, force=force, render=True)])
            env_vec = VecNormalize.load(vec_path_2, env)
            #  do not update them at test time
            env_vec.training = False
            # reward normalization is not needed at test time
            env_vec.norm_reward = False

            model = PPO.load(model_name)
            # Set camera to follow the robot

            # Custom evaluation of the model
            n_eval_episodes = 5
            episode_rewards = []
            episode_distances = []
            max_episode_distances = []
            episode_times = []
            num_episodes = 0

            raw_env = env_vec.envs[0]

            print("\nStarting evaluation over multiple episodes...\n")
            for ep in range(n_eval_episodes):
                ep_rewards = []

                max_distance = 0.0
                last_distance = 0.0
                final_reward = 0.0
                elapsed_steps = 0
                obs = env_vec.reset()
                raw_env.let_robot_fall()
                done = False
                while not done:
                    action, _ = model.predict(obs, deterministic=False)
                    obs, reward, terminated, infos = env_vec.step(action)
                    #print(reward)
                    ep_rewards.append(reward)
                    robot_pos = raw_env.getRobotPosition()
                    p.resetDebugVisualizerCamera(cameraDistance=1,
                                                 cameraYaw=50,
                                                 cameraPitch=-30,
                                                 cameraTargetPosition=robot_pos)
                    r = float(reward[0]) if isinstance(reward, (list, tuple, np.ndarray)) else float(reward)
                    term = bool(terminated[0]) if isinstance(terminated, (list, tuple, np.ndarray)) else bool(
                        terminated)

                    info = infos[0] if isinstance(infos, (list, tuple)) and len(infos) > 0 else (
                        infos if isinstance(infos, dict) else {})
                    dist = float(info.get("total_distance", last_distance))
                    # --- keep final step reward (overwrite each step) ---
                    final_reward = r

                    # --- distances ---
                    last_distance = dist
                    if dist > max_distance:
                        max_distance = dist

                    # --- steps/time ---
                    elapsed_steps = int(info.get("elapsed_steps", elapsed_steps))

                    done = terminated

                print(f"Episode {ep + 1} Final Reward: {max_distance:.2f}")

                # --- store per-episode results ---
                #print(np.mean(ang_speed_collect))
                max_episode_distances.append(max_distance)
                episode_rewards.append(final_reward)
                episode_distances.append(last_distance)
                episode_times.append(elapsed_steps)
                num_episodes += 1

            mean_reward = np.mean(episode_rewards)
            std_reward = np.std(episode_rewards)
            median = np.median(episode_rewards)

            print(f"\nEvaluation over {n_eval_episodes} episodes: mean_reward = {mean_reward:.2f} +/- {std_reward:.2f}")
            print(f"\nEvaluation over {n_eval_episodes} episodes: median = {median:.2f}")


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
        # plt.figure(figsize=(10, 5))
        # plt.plot(range(1, len(episode_rewards) + 1), episode_rewards, marker="o", label="Episode Reward")
        # plt.axhline(avg_reward, color="g", linestyle="--", label=f"Avg Reward ({avg_reward:.2f})")
        # plt.fill_between(range(1, len(episode_rewards) + 1),
        #                  avg_reward - std_reward,
        #                  avg_reward + std_reward,
        #                  color="g", alpha=0.2, label="±1 Std Dev")
        # plt.title("Episode Rewards")
        # plt.xlabel("Episode")
        # plt.ylabel("Reward")
        # plt.legend()
        # plt.grid(True, linestyle=":", alpha=0.7)
        # plt.tight_layout()
        # plt.show()

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

        env_vec.close()

