import os
import numpy as np
import matplotlib.pyplot as plt
from stable_baselines3 import PPO
from sge_FOR_ER.sge.sge.Env_mars import URDFRobotEnv
import pybullet as p

from stable_baselines3.common.vec_env import VecNormalize, DummyVecEnv
"""
:::::::::::::::::: EVALUATE THE ROBOT AND ITS CONTROLLER :::::::::::::::::: 
"""
# Ensure results directory exists
results_dir = "evaluation_results"
os.makedirs(results_dir, exist_ok=True)

forces = [15]
velocities = [67]


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
            #vec_path_2 = f"./models_PPO_Test_NEW_REWARD/best_gen_020_sem_castigo_distancia_tStep.pkl"
            #model_name = f"./models_PPO_Test_NEW_REWARD/best_gen_020_sem_castigo_distancia_tStep"


            vec_path_2 = f"./models_PPO_Test_NEW_REWARD/best_gen_020_sem_castigo_distancia_tStep_horizontal.pkl"
            ROBOT_URDF_PATH_sim = f"./models_PPO_Test_NEW_REWARD/best_gen_020_simetrico_geracoes.urdf"  # ESTE É O ROBO
            ROBOT_URDF_PATH = f"./models_PPO_Test_NEW_REWARD/best_gen_020.urdf"
            model_name = f"./models_PPO_Test_NEW_REWARD/best_gen_020_sem_castigo_distancia_tStep_horizontal"

            # # Ensure the model file exists
            # if not os.path.exists(model_name):
            #     print(f"Model {model_name} not found. Skipping...")
            #     continue
            env = DummyVecEnv([URDFRobotEnv_make(ROBOT_URDF_PATH, velocity=velocity, force=force, render=True)])
            env_vec = VecNormalize.load(vec_path_2, env)
            #  do not update them at test time
            env_vec.training = False
            # reward normalization is not needed at test time
            env_vec.norm_reward = False

            model = PPO.load(model_name)
            # Set camera to follow the robot

            # Custom evaluation of the model
            n_eval_episodes = 30
            episode_rewards = []
            episode_distances = []
            max_episode_distances = []
            episode_times = []
            num_episodes = 0

            raw_env = env_vec.envs[0]

            print("\nStarting evaluation over multiple episodes...\n")
            for ep in range(n_eval_episodes):
                max_distance = 0.0
                last_distance = 0.0
                final_reward = 0.0
                elapsed_steps = 0
                ep_rewards = []

                obs = env_vec.reset()
                raw_env.let_robot_fall()
                done = False
                while not done:
                    robot_pos = raw_env.getRobotPosition()
                    p.resetDebugVisualizerCamera(cameraDistance=0.5,
                                                 cameraYaw=50,
                                                 cameraPitch=-10,
                                                 cameraTargetPosition=robot_pos)
                    action, _ = model.predict(obs, deterministic=False)
                    obs, reward, terminated, infos = env_vec.step(action)

                    # --- safe unpacking for VecEnv ---
                    r = float(reward[0]) if isinstance(reward, (list, tuple, np.ndarray)) else float(reward)
                    term = bool(terminated[0]) if isinstance(terminated, (list, tuple, np.ndarray)) else bool(
                        terminated)
                    info = infos[0] if isinstance(infos, (list, tuple)) and len(infos) > 0 else (
                        infos if isinstance(infos, dict) else {})

                    # --- keep final step reward (overwrite each step) ---
                    final_reward = r

                    # --- distances ---
                    dist = float(info.get("total_distance", last_distance))
                    last_distance = dist
                    if dist > max_distance:
                        max_distance = dist

                    # --- steps/time ---
                    elapsed_steps = int(info.get("elapsed_steps", elapsed_steps))

                    done = term

                print(f"Episode {ep + 1} Final Reward: {final_reward:.2f} | "
                      f"Last Distance: {last_distance:.3f} | Max Distance: {max_distance:.3f}")

                # --- store per-episode results ---
                max_episode_distances.append(max_distance)
                episode_rewards.append(final_reward)
                episode_distances.append(last_distance)
                episode_times.append(elapsed_steps)
                num_episodes += 1


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

