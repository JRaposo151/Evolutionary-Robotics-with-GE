import time
from stable_baselines3 import PPO
from Env import URDFRobotEnv
import pybullet as p
from stable_baselines3.common.evaluation import evaluate_policy

"""
:::::::::::::::::: EVALUATE THE ROBOT AND ITS CONTROLLER :::::::::::::::::: 
"""

# Define the robot environment
startOrientation = p.getQuaternionFromEuler([0, 0, 0])
startPos = [0, 0, 0.5]
flags = p.URDF_USE_SELF_COLLISION


# Open the file for writing the results
with open('evaluation_results.txt', 'w') as f:
    f.write("Evaluation Results:\n")

    # Run evaluation 11 times for models 'ppo_robot1.zip' to 'ppo_robot11.zip'
    for i in range(11):  # Iterate 11 times
        ROBOT_URDF_PATH = f"/home/joaoraposo/Documents/GitHub/Evolutionary-Robotics-with-GE/corrected_robot{i}.urdf"
        env = URDFRobotEnv(ROBOT_URDF_PATH, startPos, startOrientation, flags,render=True)  # Set render=True to visualize

        model_name = f"ppo_robot{2}.zip"
        model = PPO.load(model_name)  # Load the model

        obs = env.reset()
        env.let_robot_fall()

        # Test the trained model
        for _ in range(2000):  # Run for 2000 steps (~8 seconds at 240Hz)
            action, _ = model.predict(obs, deterministic=True)  # Get action from PPO
            obs, reward, done, _ = env.step(action)
            robot_pos = env.getRobotPosition()

            # Set camera to follow the robot
            p.resetDebugVisualizerCamera(cameraDistance=1.5,
                                         cameraYaw=50,
                                         cameraPitch=-30,
                                         cameraTargetPosition=robot_pos)
            print(reward)
            print(done)

            time.sleep(1.0 / 60.0)  # Slow down simulation (60 FPS)
            if done:
                print("CHEGOU AQUI")
                obs = env.reset()
                env.close()

        # Evaluate the model
        mean_reward, std_reward = evaluate_policy(model, env, n_eval_episodes=10, deterministic=True)

        # Write the results to the file
        f.write(f"Model {i} ({model_name}):\n")
        f.write(f"  mean_reward={mean_reward:.2f} +/- {std_reward}\n")
        print(f"Model {i}: mean_reward={mean_reward:.2f} +/- {std_reward}")  # Also print the results in the console

