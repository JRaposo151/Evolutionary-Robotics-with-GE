#!/usr/bin/env python3
"""
PyBullet Husky torque-control demo (go forward along +Y) for ~4800 timesteps.

Notes:
- Husky uses 4 wheel joints. We apply TORQUE_CONTROL directly.
- We disable the default velocity motors first.
- We keep torque signs consistent so it drives forward in +Y (you can flip signs if it moves backward).
"""
import os
import time
import pybullet as p
import pybullet_data
from sge_FOR_ER.sge.sge import new_mart_terrain
import numpy as np

# ---- Config ----
DT = 1.0 / 240.0
STEPS = 8000

# Torque magnitude per wheel (tune up/down)
TORQUE = 15.0
TORQUE_OWN_ROBOT = 15



def main():
    own_robots = True
    movable_joints = []


    flags = p.URDF_USE_SELF_COLLISION
    p.connect(p.GUI)
    p.setAdditionalSearchPath(pybullet_data.getDataPath())
    p.setPhysicsEngineParameter(enableFileCaching=0)  # Avoid caching old URDFs
    # Show contact points in PyBullet
    p.setPhysicsEngineParameter(enableConeFriction=1)  # Improve friction
    p.setPhysicsEngineParameter(enableSAT=1)  # Use SAT solver for better collisions
    p.setGravity(0, 0, -9.81)
    p.setTimeStep(DT)
    # Ground
    plane = new_mart_terrain.world_generation()
    p.setAdditionalSearchPath(pybullet_data.getDataPath())
    p.changeDynamics(plane, -1, lateralFriction=0.5)

    if not own_robots:
        path = "husky/husky.urdf"
        ori = [0, 0, 0.7071, 0.7071]
        pos = [65, 75, 10]

        husky_id = p.loadURDF(path, pos, ori, useFixedBase=False, flags=flags)
        # Husky
        # Identify wheel joints by name (robust)
        wheel_joint_names = {
            "front_left_wheel",
            "front_right_wheel",
            "rear_left_wheel",
            "rear_right_wheel",
        }

        wheel_joints = []
        for j in range(p.getNumJoints(husky_id)):
            info = p.getJointInfo(husky_id, j)
            jname = info[1].decode("utf-8")
            if jname in wheel_joint_names:
                wheel_joints.append(j)

        print("Wheel joints:", wheel_joints)

        # Disable default motors so TORQUE_CONTROL works as expected
        # for j in wheel_joints:
        #      p.setJointMotorControl2(husky_id, j, controlMode=p.VELOCITY_CONTROL,targetVelocity=0, force=0)

        # Camera
        p.resetDebugVisualizerCamera(
            cameraDistance=2.0,
            cameraYaw=60,
            cameraPitch=-25,
            cameraTargetPosition=[0, 0, 0.2],
        )
        for _ in range(150):
            p.stepSimulation()
        # Run simulation
        for step in range(STEPS):
            base_pos, _ = p.getBasePositionAndOrientation(husky_id)

            # Keep camera following the robot
            p.resetDebugVisualizerCamera(
                cameraDistance=2.0,
                cameraYaw=60,
                cameraPitch=-25,
                cameraTargetPosition=base_pos,
            )

            for j in wheel_joints:
                # p.setJointMotorControl2(
                #     bodyUniqueId=husky_id,
                #     jointIndex=j,
                #     controlMode=p.TORQUE_CONTROL,
                #     force=float(TORQUE),
                # )



                p.setJointMotorControl2(husky_id, j, p.VELOCITY_CONTROL,
                                         targetVelocity=-11.3, force=TORQUE)

            p.stepSimulation()
            lin_vel, _ = p.getBaseVelocity(husky_id)
            vx, vy, vz = lin_vel
            speed = (vx * vx + vy * vy + vz * vz) ** 0.5
            print(f"vx={vx:.3f} vy={vy:.3f} speed={speed:.3f} ")

            for wheel_id in wheel_joints:
                state = p.getJointState(husky_id, wheel_id)

                actual_velocity = state[1]
                applied_torque = state[3]

                print(f"Roda {wheel_id} | Velocidade: {actual_velocity:.2f} rad/s | Torque: {applied_torque:.2f} Nm")


            time.sleep(DT)

        p.disconnect()

    else:
        ori = np.array(p.getQuaternionFromEuler([0, 0, 1.5]))
        path = "/home/joaoraposo/Documents/GitHub/Evolutionary-Robotics-with-GE/Controller_testing/models_PPO_Test_NEW_REWARD/best_gen_020.urdf"
        husky_id = p.loadURDF(path, np.array([65, 75, 8.5]), ori, useFixedBase=False, flags=flags)

        for joint in range(p.getNumJoints(husky_id)):
            joint_info = p.getJointInfo(husky_id, joint)
            link_name = p.getJointInfo(husky_id,joint)
            print(joint, joint_info[12].decode("utf-8"))
            #if "wheel_link" in joint_info[12].decode("utf-8"):
                #p.changeDynamics(husky_id, joint, lateralFriction=1)

            # Identify revolute joints with limits
            if p.getJointInfo(husky_id, joint)[2] in [0]:
                movable_joints.append(joint)

        num_movable_joints = len(movable_joints)
        print(f"Number of Movable Joints: {num_movable_joints}")

        for i in range(p.getNumJoints(husky_id)):
            joint_info = p.getJointInfo(husky_id, i)
            link_name = joint_info[12].decode("utf-8")

            # Disable ALL collisions for links that are just visual joints
            if "L_joint_" in link_name or "Sphere_" in link_name or "B_joint" in link_name:
                link_index = joint_info[0]
                p.setCollisionFilterGroupMask(husky_id, link_index, collisionFilterGroup=0, collisionFilterMask=0)
# Disable default motors so TORQUE_CONTROL works as expected

        # Camera
        p.resetDebugVisualizerCamera(
            cameraDistance=2.0,
            cameraYaw=60,
            cameraPitch=-25,
            cameraTargetPosition=[0, 0, 0.2],
        )
        for _ in range(150):
            p.stepSimulation()
        # Run simulation
        for step in range(STEPS):

            base_pos, base_ori = p.getBasePositionAndOrientation(husky_id)
            lin_vel, ang_vel = p.getBaseVelocity(husky_id)
            ang_speed = np.linalg.norm(ang_vel)
            base_ori = p.getEulerFromQuaternion(base_ori)
            print(ang_speed)
            # Keep camera following the robot
            p.resetDebugVisualizerCamera(
                cameraDistance=2.0,
                cameraYaw=60,
                cameraPitch=-25,
                cameraTargetPosition=base_pos,
            )

            for i, j in enumerate(movable_joints):
                #p.setJointMotorControl2(husky_id, j, controlMode=p.VELOCITY_CONTROL, force=0)

                if i % 2 == 0:
                    # p.setJointMotorControl2(
                    #     bodyUniqueId=husky_id,
                    #     jointIndex=j,
                    #     controlMode=p.TORQUE_CONTROL,
                    #     force=float(-TORQUE_OWN_ROBOT),
                    # )

                    p.setJointMotorControl2(husky_id, j, p.VELOCITY_CONTROL,
                                            targetVelocity=-67, force=TORQUE_OWN_ROBOT)
                else:
                #     p.setJointMotorControl2(
                #         bodyUniqueId=husky_id,
                #         jointIndex=j,
                #         controlMode=p.TORQUE_CONTROL,
                #         force=float(TORQUE_OWN_ROBOT),
                #     )

                    p.setJointMotorControl2(husky_id, j, p.VELOCITY_CONTROL,
                                            targetVelocity=67, force=TORQUE_OWN_ROBOT)

            p.stepSimulation()

            lin_vel, _ = p.getBaseVelocity(husky_id)
            vx, vy, vz = lin_vel
            speed = (vx * vx + vy * vy + vz * vz) ** 0.5
            print(f"vx={vx:.3f} vy={vy:.3f} speed={speed:.3f} ")

            for wheel_id in movable_joints:
                state = p.getJointState(husky_id, wheel_id)

                actual_velocity = state[1]
                applied_torque = state[3]

                print(f"Roda {wheel_id} | Velocidade: {actual_velocity:.2f} rad/s | Torque: {applied_torque:.2f} Nm")

            time.sleep(DT)

        p.disconnect()


if __name__ == "__main__":
    main()
