import os
import numpy as np
import matplotlib.pyplot as plt
from stable_baselines3 import PPO
from sge_FOR_ER.sge.sge.Env_mars import URDFRobotEnv
import pybullet as p
from stable_baselines3.common.vec_env import VecNormalize, DummyVecEnv


def URDFRobotEnv_make(ROBOT_URDF_PATH, velocity, force, render, plane):
    def _init():
        if plane == 0:
            from sge_FOR_ER.sge.sge.Env_horizontal import URDFRobotEnv
            env = URDFRobotEnv(ROBOT_URDF_PATH, velocity, force, render=render)
        elif plane == 1:
            from sge_FOR_ER.sge.sge.Env_mars import URDFRobotEnv
            env = URDFRobotEnv(ROBOT_URDF_PATH, velocity, force, render=render)
        return env
    return _init

def test(PATH, name, plane):

    """
    :::::::::::::::::: EVALUATE THE ROBOT AND ITS CONTROLLER ::::::::::::::::::
    """
    # Ensure results directory exists
    results_dir = "evaluation_results"
    os.makedirs(results_dir, exist_ok=True)
    model_path = f"robots_brains/{name}.zip"
    vec_path = f"robots_vec/{name}.pkl"

    # Open the file for writing evaluation results
    with open(os.path.join(results_dir, "evaluation_results.txt"), 'w') as f:
        f.write("Evaluation Results:\n\n")
        env = DummyVecEnv([URDFRobotEnv_make(PATH, velocity=67, force=15,  render=False, plane=plane)])
        env_vec = VecNormalize.load(vec_path, env)
        #  do not update them at test time
        env_vec.training = False
        # reward normalization is not needed at test time
        env_vec.norm_reward = False
        model = PPO.load(model_path)
        n_eval_episodes = 3
        episode_rewards = []
        raw_env = env_vec.envs[0]

        print("\nStarting evaluation over multiple episodes...\n")
        for ep in range(n_eval_episodes):
            ep_rewards = []
            obs = env_vec.reset()
            raw_env.let_robot_fall()
            done = False
            while not done:
                action, _ = model.predict(obs, deterministic=False)
                obs, reward, terminated, _ = env_vec.step(action)
                ep_rewards.append(reward)
                robot_pos = raw_env.getRobotPosition()
                # p.resetDebugVisualizerCamera(cameraDistance=1,
                #                              cameraYaw=50,
                #                              cameraPitch=-30,
                #                              cameraTargetPosition=robot_pos)
                done = terminated

            episode_total = ep_rewards[-1][0]
            episode_rewards.append(episode_total)
            print(f"Episode {ep + 1} Final Reward: {episode_total:.2f}")

        mean_reward = np.mean(episode_rewards)
        std_reward = np.std(episode_rewards)
        median = np.median(episode_rewards)

        print(f"\nEvaluation over {n_eval_episodes} episodes: mean_reward = {mean_reward:.2f} +/- {std_reward:.2f}")
        print(f"\nEvaluation over {n_eval_episodes} episodes: median = {median:.2f}")

        # -------------------------
        # Write the results to the file
        f.write(f"Model {name} Velocity: {67} Force: {15} ZIP: {model_path}.zip")
        f.write(f" Median Reward = {mean_reward:.2f}")

        # Clean up
        obs = env_vec.reset()
        env_vec.close()

    return median