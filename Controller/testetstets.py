import optuna
import numpy as np
import os
import numpy as np
import matplotlib.pyplot as plt
from stable_baselines3 import PPO
from Env import URDFRobotEnv
import pybullet as p

"""
:::::::::::::::::: EVALUATE THE ROBOT AND ITS CONTROLLER :::::::::::::::::: 
"""
walker = os.walk("models_PPO_Test")

# Define simulation parameters
startOrientation = p.getQuaternionFromEuler([0, 0, 0])
startPos = [0, 0, 0.2]
flags = p.URDF_USE_SELF_COLLISION_EXCLUDE_PARENT

dt = 1 / 240.0  # Simulation timestep
# total_simulated_time = 20  # Simulate 20 virtual seconds
# num_steps = int(total_simulated_time / dt)  # Total simulation steps

# Ensure results directory exists
results_dir = "evaluation_results"
os.makedirs(results_dir, exist_ok=True)


def objective(trial):
    # Sugere valores para velocidade e força
    velocity = trial.suggest_float('velocity', 0.5, 5.0)  # Exemplo: busca entre 0.5 e 5 rad/s
    force = trial.suggest_float('force', 5.0, 30.0)  # Exemplo: busca entre 5 e 30 Nm

    # Aqui, você deve integrar com o seu ambiente e controlador.
    # Por exemplo, você pode criar o ambiente com esses parâmetros:
    env = URDFRobotEnv(ROBOT_URDF_PATH, startPos, startOrientation, flags, velocity, force, render=False)

    # Carrega o modelo (ou treina, se necessário) – ou apenas execute uma avaliação
    model = PPO.load(f"models_PPO_Test/testVandF_robot{some_index}.zip")

    # Execute uma avaliação com n episódios e calcule a média de recompensa
    n_eval_episodes = 5
    episode_rewards = []
    for ep in range(n_eval_episodes):
        obs, _ = env.reset()
        env.let_robot_fall()
        done = False
        ep_reward = 0
        while not done:
            action, _ = model.predict(obs, deterministic=False)
            obs, reward, terminated, truncated, _ = env.step(action)
            ep_reward += reward
            done = terminated or truncated
        episode_rewards.append(ep_reward)

    mean_reward = np.mean(episode_rewards)

    # Retorne o valor negativo se queremos maximizar a recompensa (pois o Optuna minimiza a função objetivo)
    return -mean_reward


study = optuna.create_study()
study.optimize(objective, n_trials=20)

print("Melhores parâmetros:", study.best_params)
print("Melhor recompensa:", -study.best_value)
