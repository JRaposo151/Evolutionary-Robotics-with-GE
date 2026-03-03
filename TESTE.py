#!/usr/bin/env python3
import time
import os
import pybullet as p
import pybullet_data

# ----------------------------
# Config
# ----------------------------
DT = 1.0 / 240.0
TOTAL_SEC = 20.0

# Fixed in the air
START_POS = [0, 0, 0.8]
START_ORN = p.getQuaternionFromEuler([0, 0, 0])

# Position-control settings
FORCE = 60.0
AMP = 0.6                 # radians (safe-ish default)
HOLD_NEG_SEC = 0.5
HOLD_POS_SEC = 0.5
TRANSITION_SEC = 0.2

# Laikago URDF inside pybullet_data
LAIKAGO_URDF = "laikago/laikago_toes.urdf"  # common in pybullet_data; fallback below if missing


def load_laikago():
    """Try common laikago URDF paths in pybullet_data."""
    candidates = [
        "laikago/laikago_toes.urdf",
        "laikago/laikago.urdf",
    ]
    for rel in candidates:
        abs_path = os.path.join(pybullet_data.getDataPath(), rel)
        if os.path.exists(abs_path):
            return rel
    raise FileNotFoundError("Could not find laikago URDF in pybullet_data (tried laikago_toes.urdf and laikago.urdf).")


def main():
    p.connect(p.GUI)
    p.setAdditionalSearchPath(pybullet_data.getDataPath())
    p.setGravity(0, 0, -9.8)
    p.setTimeStep(DT)
    p.loadURDF("plane.urdf")

    urdf_rel = load_laikago()
    laikago_id = p.loadURDF(urdf_rel, START_POS, START_ORN, useFixedBase=True)

    # ----------------------------
    # Select joints that are NOT "continuous" by NAME (revolute only)
    # ----------------------------
    non_continuous = []
    for j in range(p.getNumJoints(laikago_id)):
        info = p.getJointInfo(laikago_id, j)
        jtype = info[2]
        joint_name = info[1].decode("utf-8").lower()
        link_name = info[12].decode("utf-8").lower()
        if jtype == p.JOINT_REVOLUTE:
            if ("continuous" not in joint_name) and ("continuous" not in link_name):
                non_continuous.append(j)

    print("Loaded:", urdf_rel)
    print("Total joints:", p.getNumJoints(laikago_id))
    print("Non-continuous joints (by name):", non_continuous)
    print("Count:", len(non_continuous))

    # Camera
    p.resetDebugVisualizerCamera(
        cameraDistance=1.5,
        cameraYaw=45,
        cameraPitch=-25,
        cameraTargetPosition=[START_POS[0], START_POS[1], START_POS[2] - 0.3],
    )

    # Helpers
    def set_joints(target_pos: float):
        for j in non_continuous:
            p.setJointMotorControl2(
                bodyIndex=laikago_id,
                jointIndex=j,
                controlMode=p.POSITION_CONTROL,
                targetPosition=float(target_pos),
                force=float(FORCE),
            )

    def ramp(from_pos: float, to_pos: float, duration_sec: float):
        steps = max(1, int(duration_sec / DT))
        for k in range(steps):
            a = (k + 1) / steps
            target = (1 - a) * from_pos + a * to_pos
            set_joints(target)
            p.stepSimulation()
            time.sleep(DT)

    def hold(pos: float, duration_sec: float):
        steps = max(1, int(duration_sec / DT))
        for _ in range(steps):
            set_joints(pos)
            p.stepSimulation()
            time.sleep(DT)

    # Run alternating -AMP / +AMP
    t_end = time.time() + TOTAL_SEC
    hold(0.0, 0.25)

    while time.time() < t_end:
        hold(-AMP, HOLD_NEG_SEC)
        ramp(-AMP, +AMP, TRANSITION_SEC)
        hold(+AMP, HOLD_POS_SEC)
        ramp(+AMP, -AMP, TRANSITION_SEC)

    p.disconnect()


if __name__ == "__main__":
    main()