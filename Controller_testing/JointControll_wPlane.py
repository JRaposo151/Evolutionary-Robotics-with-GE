#!/usr/bin/env python3
import time
import pybullet as p
from Env_plane_1 import URDFRobotEnv

forces = [0.5]
velocities = [5]

ROBOT_URDF_PATH = "./models_PPO_Test_NEW_REWARD/bigger_urdf_husky.urdf"
N_STEPS = 4800
DT_SLEEP = 1.0 / 240.0

def main():
    action = [1, 1, 1, 1, 1]  # length must match env.movable_joints

    for torque_amp in forces:
        for target_vel in velocities:
            print("------------- ------------- ------------- ------------- ")
            print(f"Manual wheel test | torque_amp={torque_amp} | target_vel={target_vel}")
            print("------------- ------------- ------------- ------------- ")

            # Create env (same scenario loader)
            env = URDFRobotEnv(ROBOT_URDF_PATH, v=target_vel, f=torque_amp, render=True, plane=1)

            _ = env.reset()

            for step in range(N_STEPS):
                # camera follow
                robot_pos = env.getRobotPosition()
                p.resetDebugVisualizerCamera(
                    cameraDistance=1,
                    cameraYaw=50,
                    cameraPitch=-30,
                    cameraTargetPosition=robot_pos
                )

                # Apply actions to each movable joint
                for i, joint in enumerate(env.movable_joints):
                    joint_info = p.getJointInfo(env.roboID, joint)
                    joint_type_str = joint_info[12].decode("utf-8")  # link name in your code; ok as a heuristic
                    if "continuous" in joint_type_str:
                        # Disable default velocity motor, then apply torque
                        p.setJointMotorControl2(env.roboID, joint, p.VELOCITY_CONTROL, force=0.0)
                        p.setJointMotorControl2(env.roboID, joint, p.TORQUE_CONTROL, force=0)
                    else:
                        for _ in range(3000):
                            p.setJointMotorControl2(env.roboID, joint, p.POSITION_CONTROL, targetPosition=action[i]*10,
                                                    force=30)
                            p.stepSimulation()
                            p.setJointMotorControl2(env.roboID, joint, p.POSITION_CONTROL, targetPosition=-action[i]*10,
                                                    force=30)
                            p.stepSimulation()

                            robot_pos = env.getRobotPosition()
                            p.resetDebugVisualizerCamera(
                                cameraDistance=1,
                                cameraYaw=50,
                                cameraPitch=-30,
                                cameraTargetPosition=robot_pos
                            )

                # IMPORTANT: advance physics
                p.stepSimulation()
                time.sleep(100)


            env.close()

if __name__ == "__main__":
    main()
