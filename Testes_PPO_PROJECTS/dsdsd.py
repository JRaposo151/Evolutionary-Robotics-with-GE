import TestDog_TORQUE_4ENV
import Test_DOG_1ENV
import Test_DOG_NEW_REWARD
import TestCar_TORQUE
import TESTE_PPO_DOG



if __name__ == "__main__":
    TestCar_TORQUE.torque()
    # TESTE_PPO_DOG.position()
    #TestDog_TORQUE_4ENV.velocity() # obs e reward linha 190, linha 193
    #Test_DOG_1ENV.velocity() # tem 53 no obs
    # Test_DOG_NEW_REWARD.velocity() # linha26,






    # path = "laikago/laikago_toes.urdf"
    # flags = p.URDF_USE_SELF_COLLISION
    # path = path
    #
    # p.connect(p.GUI)
    #
    # p.setAdditionalSearchPath(pybullet_data.getDataPath())
    # p.setPhysicsEngineParameter(enableFileCaching=0)  # Avoid caching old URDFs
    # # Show contact points in PyBullet
    # p.setPhysicsEngineParameter(enableConeFriction=1)  # Improve friction
    # p.setPhysicsEngineParameter(enableSAT=1)  # Use SAT solver for better collisions
    #
    # p.setGravity(0, 0, -9.8)
    # plane = p.loadURDF("plane.urdf")
    # useFixedBase = False
    #
    # ori = [0, 0.5, 0.5, 0]
    # pos = [0, 0, 0]
    #
    # robot = p.loadURDF(path, [0, 0, 0.5],ori, useFixedBase=useFixedBase, flags=flags)
    # let_robot_fall()
    # for j in range(p.getNumJoints(robot)):
    #     info = p.getJointInfo(robot, j)
    #     joint_index = info[0]
    #     joint_name = info[1].decode("utf8")
    #     link_name = info[12].decode("utf8")  # index 12 is link name
    #     print(f"joint {joint_index:2d}: {joint_name:20s} → link {link_name}")
    # foot_links = [3, 7, 11, 15]
    # contacts = p.getContactPoints(bodyA=robot, bodyB=plane)
    # # contacts is a list of tuples. Each tuple’s 4th element is linkIndexA.
    # contact_flags = {link: 0 for link in foot_links}
    # for pt in contacts:
    #     link_idx = pt[3]  # link index on bodyA
    #     if link_idx in contact_flags:
    #         contact_flags[link_idx] = 1
    #
    # # now build a 4‐vector in a consistent order:
    # foot_contact_vector = np.array(
    #     [contact_flags[link] for link in foot_links],
    #     dtype=np.float32
    # )
    #
    # print(foot_contact_vector)

