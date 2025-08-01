import os
import random
import shutil
import xml.etree.ElementTree as ET
from bigtree import preorder_iter
from pathlib import Path
import pybullet as p
import pybullet_data
import time


simetry_activated = False
class SphereCounter:
    def __init__(self):
        self.sphere_N = 0  # Initial counter

    @property
    def sphere_name(self):
        return f"Sphere_{self.sphere_N}"  # Automatically updates

class Limb_BlackSphereCounter:
    def __init__(self):
        self.blackSphere_N = 0  # Initial counter

    @property
    def blackSphere_name(self):
        return f"blackSphere_{self.blackSphere_N}"  # Automatically updates


class Extra_SphereCounter:
    def __init__(self):
        self.Extra_N = 0  # Initial counter

    @property
    def extraSphere_name(self):
        return f"extra_sphere_{self.Extra_N}"  # Automatically updates

class JointCounter:
    def __init__(self):
        self.Joint_N = 0  # Initial counter

    @property
    def joint_name(self):
        return f"joint_{self.Joint_N}"  # Automatically updates


BASE_DIR = Path(__file__).parent
def treeFunction(file):

    piece_choice = random.choice(file)
    urdf_path = (BASE_DIR / piece_choice).resolve()
    tree = ET.parse(urdf_path)
    root = tree.getroot()
    direction = [piece_choice.split("_")[-1]]
    return root, direction[0]


def body(robot, cube_name, root):
    for child in root:
        if child.tag == "link":
            child.attrib["name"] = cube_name
        robot.append(child)
    return robot

def AuxiliarSphere(robot, cube_name, joint, sphere, root):
    for child in root:
        if child.tag == "link":
            child.attrib["name"] = sphere.sphere_name

        elif child.attrib["name"] == "joint_1":
            child.attrib["name"] = joint.joint_name
            joint.Joint_N += 1

            for sub_child in child:
                if sub_child.tag == "parent":
                    sub_child.attrib["link"] = cube_name
                elif sub_child.tag == "child":
                    sub_child.attrib["link"] = sphere.sphere_name


        robot.append(child)
    return robot


def JointRepresentation_conctBody(robot, sphere, representative_Joint, next_cube, joint, root):
    for child in root:

        if child.tag == "joint" and child.attrib["name"] == "joint_1":
            child.attrib["name"] = joint.joint_name
            joint.Joint_N += 1

            for sub_child in child:
                if sub_child.tag == "parent":
                    sub_child.attrib["link"] = sphere.sphere_name
                    sphere.sphere_N += 1
                elif sub_child.tag == "child":
                    sub_child.attrib["link"] = representative_Joint
                else:
                    break

        if root.attrib["name"] == "B_JOINT_REVO":
            if child.tag == "link":
                if child.attrib["name"] == "extra_sphere":
                    child.attrib["name"] = sphere.sphere_name
                else:
                    child.attrib["name"] = representative_Joint


            if child.tag == "joint" and child.attrib["name"] == "joint_2":
                child.attrib["name"] = joint.joint_name
                joint.Joint_N += 1

                for sub_child in child:
                    if sub_child.tag == "child":
                        sub_child.attrib["link"] = sphere.sphere_name
                    elif sub_child.tag == "parent":
                        sub_child.attrib["link"] = representative_Joint


            elif child.tag == "joint" and child.attrib["name"] == "joint_3":
                child.attrib["name"] = joint.joint_name
                joint.Joint_N += 1

                for sub_child in child:
                    if sub_child.tag == "parent":
                        sub_child.attrib["link"] = sphere.sphere_name
                        sphere.sphere_N += 1
                    elif sub_child.tag == "child":
                        sub_child.attrib["link"] = next_cube


        elif child.tag == "link":
            if child.attrib["name"]:
                child.attrib["name"] = representative_Joint

        elif child.tag == "joint" and child.attrib["name"] == "joint_2":
            child.attrib["name"] = joint.joint_name
            joint.Joint_N += 1

            for sub_child in child:
                if sub_child.tag == "child":
                    sub_child.attrib["link"] = next_cube
                elif sub_child.tag == "parent":
                    sub_child.attrib["link"] = representative_Joint
        robot.append(child)
    return robot

def JointRepresentation_conctLimb(robot, sphere, representative_Joint, blackSphere, blackSphere_name, faceSet_Covered, joint, root, sim):
    for child in root:

        if child.tag == "joint" and child.attrib["name"] == "joint_1":
            child.attrib["name"] = joint.joint_name
            joint.Joint_N += 1

            for sub_child in child:
                if sub_child.tag == "parent":
                    sub_child.attrib["link"] = sphere
                elif sub_child.tag == "child":
                    sub_child.attrib["link"] = representative_Joint

                elif sub_child.tag == "origin" and root.attrib["name"] == "L_JOINT_REVO":
                    if faceSet_Covered == "TOP":
                        sub_child.attrib["rpy"] = "0 1.55 0"
                    elif faceSet_Covered == "BOTTOM":
                        sub_child.attrib["rpy"] = "0 -1.55 0"
                    elif faceSet_Covered == "":
                        sub_child.attrib["rpy"] = "1.55 0 0"
                    elif faceSet_Covered == "FRONT" and sim:
                        sub_child.attrib["rpy"] = "0 0 3.11"

                elif sub_child.tag == "origin" and root.attrib["name"] == "L_JOINT_CONT_HZ":
                    if faceSet_Covered == "BACK":
                        if sim:
                            sub_child.attrib["rpy"] = "-1.55 0 0"
                            sub_child.attrib["xyz"] = "0 0.02 0"
                        else:
                            sub_child.attrib["rpy"] = "1.55 0 0"
                            sub_child.attrib["xyz"] = "0 -0.02 0"

                    if faceSet_Covered == "FRONT":
                        if sim:
                            sub_child.attrib["rpy"] = "1.55 0 0"
                            sub_child.attrib["xyz"] = "0 -0.02 0"
                        else:
                            sub_child.attrib["rpy"] = "-1.55 0 0"
                            sub_child.attrib["xyz"] = "0 0.02 0"

                    if faceSet_Covered == "TOP":
                        sub_child.attrib["xyz"] = "0 0 0.02"
                    if faceSet_Covered == "BOTTOM":
                        sub_child.attrib["rpy"] = "3.15 0 0"
                        sub_child.attrib["xyz"] = "0 0 -0.02 "
                    if faceSet_Covered == "RIGHT":
                        sub_child.attrib["rpy"] = "0 1.55 0"
                        sub_child.attrib["xyz"] = "0.02 0 0"
                    if faceSet_Covered == "LEFT":
                        sub_child.attrib["rpy"] = "0 -1.55 0"
                        sub_child.attrib["xyz"] = "-0.02 0 0"



                elif faceSet_Covered == "BACK":
                    if sim:
                        sub_child.attrib["rpy"] = "-1.55 0 0"
                    else:
                        sub_child.attrib["rpy"] = "1.55 0 0"
                elif faceSet_Covered == "FRONT":
                    if sim:
                        sub_child.attrib["rpy"] = "1.55 0 0"
                    else:
                        sub_child.attrib["rpy"] = "-1.55 0 0"
                elif faceSet_Covered == "LEFT":
                    sub_child.attrib["rpy"] = "0 -1.55 0"
                elif faceSet_Covered == "RIGHT":
                    sub_child.attrib["rpy"] = "0 1.55 0"
                elif faceSet_Covered == "BOTTOM":
                    sub_child.attrib["rpy"] = "0 3.15 0"




        elif child.tag == "joint" and child.attrib["name"] == "joint_2":
            child.attrib["name"] = joint.joint_name
            joint.Joint_N += 1

            for sub_child in child:
                if sub_child.tag == "child":
                    sub_child.attrib["link"] = blackSphere_name
                elif sub_child.tag == "parent":
                    sub_child.attrib["link"] = representative_Joint

                elif sub_child.tag == "origin" and root.attrib["name"] == "L_JOINT_REVO":
                    if faceSet_Covered == "RIGHT":
                        sub_child.attrib["rpy"] = "0 1.6 0"
                        sub_child.attrib["xyz"] = "0.01 0 0"
                    elif faceSet_Covered == "LEFT" or faceSet_Covered == "TOP" or faceSet_Covered == "BOTTOM":
                        sub_child.attrib["rpy"] = "0 -1.6 0"
                        sub_child.attrib["xyz"] = "-0.01 0 0"
                    elif faceSet_Covered == "FRONT":
                        sub_child.attrib["rpy"] = "-1.6 0 0"
                        sub_child.attrib["xyz"] = "0 0.01 0"
                    elif faceSet_Covered == "BACK":
                        sub_child.attrib["rpy"] = "1.6 0 0"
                        sub_child.attrib["xyz"] = "0 -0.01 0"

        elif child.tag == "link":
            child.attrib["name"] = representative_Joint

        robot.append(child)
    return robot



def limbs(robot, blackSphere, blackSphere_name, limb, extra_sphere, extra_sphere_name,  joint, root):
    for child in root:

        if child.tag == "link" and child.attrib["name"] == "":
            child.attrib["name"] = blackSphere_name

        elif child.tag == "joint" and child.attrib["name"] == "joint_1":
            child.attrib["name"] = joint.joint_name
            joint.Joint_N += 1

            for sub_child in child:
                if sub_child.tag == "parent":
                    sub_child.attrib["link"] = blackSphere_name
                    blackSphere.blackSphere_N += 1
                if sub_child.tag == "child":
                    sub_child.attrib["link"] = limb

        elif child.tag == "link" and child.attrib["name"] == "limb_link":
            child.attrib["name"] = limb

        elif child.tag == "joint" and child.attrib["name"] == "joint_2":
            child.attrib["name"] = joint.joint_name
            joint.Joint_N += 1

            for sub_child in child:
                if sub_child.tag == "parent":
                    sub_child.attrib["link"] = limb
                if sub_child.tag == "child":
                    sub_child.attrib["link"] = extra_sphere_name

        elif child.tag == "link" and (child.attrib["name"] == "limb_small_link_robot" or "limb_joint_bottom_blue_link"):
            child.attrib["name"] = extra_sphere_name

        robot.append(child)
    return robot

def save_file(file, name):
    tree = ET.ElementTree(file)
    ET.indent(tree, space="\t")
    ET.indent(tree, space="  ", level=0)
    output_folder = (BASE_DIR).resolve()
    # Ensure the output folder exists
    os.makedirs(output_folder, exist_ok=True)

    # Full path to save
    output_file = os.path.join(output_folder, name)
    tree.write(output_file, encoding="utf-8", xml_declaration=True)


def collision_test_and_commit(
    robot: ET.Element,
    testing_robot: str,
    committed_path: str,
    robot_number: int,
    node_depth: int,
    work_dir: str = "robots_test",

):
    """
    1) Writes `robot` to work_dir/testing_robot
    2) Loads into PyBullet with self-collision
    3) Steps once, checks getContactPoints()
    4) On collision: reverts `robot` ← committed_path (if exists), sets skip_until_depth
    5) On no collision: copies testing → committed_path
    6) Cleans up
    Returns: (robot, collision_found: bool, skip_until_depth: Optional[int])
    """
    # --- 1. Save URDF to disk ---
    tree = ET.ElementTree(robot)
    ET.indent(tree, space="\t")
    ET.indent(tree, space="  ", level=0)
    output_folder = f"{work_dir}/"
    os.makedirs(output_folder, exist_ok=True)
    output_path = os.path.join(output_folder, testing_robot)
    tree.write(output_path, encoding="utf-8", xml_declaration=True)
    print(f"Saved temporary URDF to {output_path}")

    # --- 2. Load into PyBullet ---
    if not p.isConnected():
        p.connect(p.DIRECT)
        p.setAdditionalSearchPath(pybullet_data.getDataPath())
        p.setGravity(0, 0, -9.8)

    robotID = p.loadURDF(
        output_path,
        useFixedBase=True,
        flags=p.URDF_USE_SELF_COLLISION
    )
    print(f"Loaded robot #{robot_number} into PyBullet (ID = {robotID})")

    # build link_names
    link_names = {}
    body_info = p.getBodyInfo(robotID)
    link_names[-1] = body_info[0].decode('utf-8')
    num_joints = p.getNumJoints(robotID)
    for j in range(num_joints):
        info = p.getJointInfo(robotID, j)
        link_names[info[0]] = info[12].decode('utf-8')

    # disable visual‐only joints
    for i in range(num_joints):
        name = p.getJointInfo(robotID, i)[12].decode('utf-8')
        if any(tag in name for tag in ("L_joint_", "Sphere_", "B_joint")):
            p.setCollisionFilterGroupMask(
                robotID, i,
                collisionFilterGroup=0,
                collisionFilterMask=0
            )

    # --- 3. Simple collision test ---
    collision_found = False
    p.stepSimulation()
    contacts = p.getContactPoints(bodyA=robotID, bodyB=robotID)
    skip_until_depth = None

    if contacts:
        collision_found = True
        skip_until_depth = node_depth
        print(f"⚠️ Self-collision detected:")
        for c in contacts:
            a, b = c[3], c[4]
            nameA = link_names.get(a, f"<unknown:{a}>")
            nameB = link_names.get(b, f"<unknown:{b}>")
            print(f"- Link {a} (“{nameA}”) ↔ Link {b} (“{nameB}”)")

        # revert to last committed if it exists
        if os.path.exists(committed_path):
            committed_tree = ET.parse(committed_path)
            robot = committed_tree.getroot()
            print(f"🔄 Reverted to committed URDF at {committed_path}")
        else:
            print(f"❌ No committed URDF at {committed_path} to revert to.")

    else:
        print("✅ No self-collisions detected in the test interval.")
        shutil.copyfile(output_path, committed_path)
        print(f"Promoted working URDF → {committed_path}")

    # --- 4. Cleanup ---
    p.removeBody(robotID)
    print(f"Removed robot {robotID} from PyBullet.")
    p.disconnect()

    try:
        os.remove(output_path)
        print(f"Deleted temporary URDF file: {output_path}")
    except OSError:
        pass


    return robot, collision_found, skip_until_depth

def assemblement(robot_tree, robot_number):


    input_file_body = ["body_Link_CUBE.urdf"]

    input_file_sphereAUX = [
        "sphere_auxiliar_Link_BACK.urdf", "sphere_auxiliar_Link_BOTTOM.urdf",
        "sphere_auxiliar_Link_FRONT.urdf", "sphere_auxiliar_Link_LEFT.urdf",
        "sphere_auxiliar_Link_RIGHT.urdf", "sphere_auxiliar_Link_TOP.urdf"
    ]

    faceSet_Covered = {}
    z_axis = []
    x_axis = []
    cube_SIM = []
    sphere = SphereCounter()
    blackSphere = Limb_BlackSphereCounter()
    extra_sphere = Extra_SphereCounter()
    direction_occupied = ""
    joint = JointCounter()
    global simetry_activated
    simetry_activated = False
    pass_cube = False
    sim_check = False

    print("Assembling Started: ")

    # Robot file creation
    print(f"Robot number: {robot_number} being assembled...")
    robot = ET.Element("robot", name=f"combined_robot_{robot_number}")
    symmetry_part = ET.Element("robot", name=f"sim")
    skip_until_depth = None
    turn_sim_off_node = 0
    testing_robot = "copy_robot.urdf"
    output_file = f"robot_{robot_number}.urdf"  # Modified URDF for each iteration
    cube = ""



    for node in preorder_iter(robot_tree):
        if pass_cube:
            if skip_cube is not None and node.depth > skip_cube:
                continue
            skip_cube = None
            pass_cube = False
        if robot_number == "GEN_0_number_56" :
            print("A")
        # if we’re in “skip mode” and still below the skip depth, keep skipping
        if skip_until_depth is not None and node.depth > skip_until_depth:
            continue
        if skip_until_depth is not None and node.depth <= skip_until_depth:
            skip_until_depth = None
        if (turn_sim_off_node >= node.depth and simetry_activated):
            turn_sim_off_node = 0
            save_file(symmetry_part, "simetry.urdf")
            simetry_activated = False
            root, _ = treeFunction(["simetry.urdf"])
            for child in root:
                robot.append(child)
            symmetry_part = ET.Element("robot", name="sim")
            committed_path = "robots_test/robot_update_free_Colision.urdf"
            robot, collision_found, skip_until_depth = collision_test_and_commit(
                robot,
                testing_robot,
                committed_path,
                robot_number,
                node.depth,
            )
            sim_check = False
            if skip_until_depth is not None:
                skip_until_depth = None

        if sim_check:
            save_file(symmetry_part, "simetry.urdf")
            root, _ = treeFunction(["simetry.urdf"])
            for child in root:
                robot.append(child)
            symmetry_part = ET.Element("robot", name="sim")
            committed_path = "robots_test/robot_update_free_Colision.urdf"
            robot, collision_found, skip_until_depth = collision_test_and_commit(
                robot,
                testing_robot,
                committed_path,
                robot_number,
                node.depth,
            )
            sim_check = False
            if skip_until_depth is not None:
                skip_until_depth = None


        # for each node in the tree, it will be add to the robot file a component


        ## HERE IS THE BODY CONSTRUCTION
        if node.node_name.__contains__("body_Link_CUBE"):
            root, _ = treeFunction(input_file_body)  # in this case, the direction doesn t matter
            print(node.node_name)
            robot = body(robot, node.node_name, root)
            faceSet_Covered[node.node_name] = []
            j = node.parent
            if node.node_name == "0 body_Link_CUBE":
                faceSet_Covered[node.node_name].append("BACK")
                z_axis.append(node.node_name)
                x_axis.append(node.node_name)
            if not node.parent.node_name == "0 ROOT":
                if (z_axis.__contains__(j.parent.node_name) or x_axis.__contains__(j.parent.node_name)) and faceSet_Covered[j.parent.node_name][-1] == "FRONT":
                    turn_sim_off_node = node.depth
                if (simetry_activated and not node.node_name == "0 body_Link_CUBE" and
                    (z_axis.__contains__(j.parent.node_name) or x_axis.__contains__(j.parent.node_name)) or cube_SIM.__contains__(j.parent.node_name)):
                    root_sim, _ = treeFunction(input_file_body)
                    symmetry_part = body(symmetry_part, f"{node.node_name}_sim", root_sim)
                    save_file(symmetry_part, "symmetry.urdf")
                    cube_SIM.append(node.node_name)


            if node.parent.node_name.__contains__("B_joint"):
                cube = node.node_name
                if direction_occupied == "LEFT":
                    faceSet_Covered[cube].append("RIGHT")
                    faceSet_Covered[cube].append("BACK")
                    j = node.parent
                    if x_axis.__contains__(j.parent.node_name):
                        x_axis.append(cube)
                    elif z_axis.__contains__(j.parent.node_name):
                        x_axis.append(cube)

                if direction_occupied == "RIGHT":
                    faceSet_Covered[cube].append("LEFT")
                    faceSet_Covered[cube].append("BACK")
                    j = node.parent
                    if x_axis.__contains__(j.parent.node_name):
                        x_axis.append(cube)
                    elif z_axis.__contains__(j.parent.node_name):
                        x_axis.append(cube)
                if direction_occupied == "TOP":
                    faceSet_Covered[cube].append("BOTTOM")
                    faceSet_Covered[cube].append("BACK")
                    j = node.parent
                    if z_axis.__contains__(j.parent.node_name):
                        z_axis.append(cube)

                if direction_occupied == "FRONT":
                    faceSet_Covered[cube].append("BACK")
                if direction_occupied == "BACK":
                    faceSet_Covered[cube].append("FRONT")
                if direction_occupied == "BOTTOM":
                    faceSet_Covered[cube].append("TOP")
                    faceSet_Covered[cube].append("BACK")
                    j = node.parent
                    if z_axis.__contains__(j.parent.node_name):
                        z_axis.append(cube)


        ## HERE IS THE AUXILIAR SPHERE CONSTRUCTION AND JOINT FOR BODY
        elif node.node_name.__contains__("B_joint"):
            cube = node.parent.node_name
            if "body_Link_CUBE" not in cube:
                continue
            if len(faceSet_Covered[cube]) == 6:
                pass_cube = True
                skip_cube = node.depth
                continue
            root, direction = treeFunction(input_file_sphereAUX)
            while True:
                if direction.split(".urdf")[0] in faceSet_Covered.get(cube, []):
                    root, direction = treeFunction(input_file_sphereAUX)
                else:
                    faceSet_Covered[cube].append(direction.split(".urdf")[0])
                    direction_occupied = direction.split(".urdf")[0]
                    break
            if (
                    (faceSet_Covered[cube][-1] == "FRONT") and node.parent.node_name == cube
                    and
                    (z_axis.__contains__(node.parent.node_name) or x_axis.__contains__(node.parent.node_name))
            ):
                simetry_activated = True
                print(node.node_name)

            if faceSet_Covered[cube][-1] == "FRONT" and z_axis.__contains__(cube):
                root_sim, direction_sim = treeFunction(['sphere_auxiliar_Link_BACK.urdf'])
            elif simetry_activated and faceSet_Covered[cube][-1] == "LEFT" :
                root_sim, direction_sim = treeFunction(['sphere_auxiliar_Link_LEFT.urdf'])
            elif simetry_activated and faceSet_Covered[cube][-1] == "RIGHT" :
                root_sim, direction_sim = treeFunction(['sphere_auxiliar_Link_RIGHT.urdf'])
            elif simetry_activated and faceSet_Covered[cube][-1] == "BOTTOM":
                root_sim, direction_sim = treeFunction(['sphere_auxiliar_Link_BOTTOM.urdf'])
            elif simetry_activated and faceSet_Covered[cube][-1] == "TOP":
                root_sim, direction_sim = treeFunction(['sphere_auxiliar_Link_TOP.urdf'])
            elif faceSet_Covered[cube][-1] == "FRONT":
                root_sim, direction_sim = treeFunction(['sphere_auxiliar_Link_BACK.urdf'])
            elif faceSet_Covered[cube][-1] == "BACK":
                root_sim, direction_sim = treeFunction(['sphere_auxiliar_Link_BACK.urdf'])

            robot = AuxiliarSphere(robot, node.parent.node_name, joint, sphere, root)
            # joint for the body
            joints = node.node_name.split(" ")
            root, direction = treeFunction([joints[-1] + "_" + direction])
            for child in node.children:
                robot = JointRepresentation_conctBody(robot, sphere, node.node_name, child.node_name, joint, root)

            if simetry_activated:
                if (z_axis.__contains__(node.parent.node_name) or x_axis.__contains__(node.parent.node_name) ):
                    try:
                        symmetry_part = AuxiliarSphere(
                            symmetry_part,
                            node.parent.node_name,
                            joint,
                            sphere,
                            root_sim
                        )
                    except UnboundLocalError as e:
                        # Print out a clear debug message:
                        print("❌ UnboundLocalError in assemblement():")
                        print(f"   Error message: {e}")
                        print("   Available local variables:")
                        for var_name, value in locals().items():
                            print(f"     - {var_name!r} = {value!r}")
                        # Optionally re-raise or handle gracefully:
                        raise
                else:
                    symmetry_part = AuxiliarSphere(symmetry_part, f"{node.parent.node_name}_sim", joint, sphere, root_sim)

                # joint for the body
                joints = node.node_name.split(" ")
                root_sim, _ = treeFunction([joints[-1] + "_" + direction_sim])
                for child in node.children:
                    symmetry_part = JointRepresentation_conctBody(symmetry_part, sphere, f"{node.node_name}_sim", f"{child.node_name}_sim", joint, root_sim)

        ## HERE IS THE LIMB JOINT CONSTRUCTION
        elif node.node_name.__contains__("L_joint"):
            cube = node.parent.node_name
            if cube.__contains__("body_Link_CUBE"):
                if len(faceSet_Covered[cube]) == 6:
                    pass_cube = True
                    skip_cube = node.depth
                    continue
            if node.parent.node_name.__contains__("body_Link_CUBE"):
                root, direction = treeFunction(input_file_sphereAUX)
                while True:
                    if direction.split(".urdf")[0] in faceSet_Covered.get(cube, []):
                        root, direction = treeFunction(input_file_sphereAUX)
                    else:
                        faceSet_Covered[cube].append(direction.split(".urdf")[0])
                        direction_occupied = direction.split(".urdf")[0]
                        break
                print(faceSet_Covered[cube][-1])
                if ((faceSet_Covered[cube][-1] == "FRONT") and node.parent.node_name == cube
                    and
                    (z_axis.__contains__(node.parent.node_name) or x_axis.__contains__(node.parent.node_name))):
                    simetry_activated = True
                    turn_sim_off_node = node.depth
                    print(node.node_name)
                    root_sim, direction_sim = treeFunction(['sphere_auxiliar_Link_BACK.urdf'])
                elif simetry_activated and faceSet_Covered[cube][-1] == "BACK":
                    root_sim, direction_sim = treeFunction(['sphere_auxiliar_Link_FRONT.urdf'])
                elif simetry_activated and faceSet_Covered[cube][-1] == "LEFT":
                    root_sim, direction_sim = treeFunction(['sphere_auxiliar_Link_LEFT.urdf'])
                elif simetry_activated and faceSet_Covered[cube][-1] == "RIGHT":
                    root_sim, direction_sim = treeFunction(['sphere_auxiliar_Link_RIGHT.urdf'])
                elif simetry_activated and faceSet_Covered[cube][-1] == "BOTTOM":
                    root_sim, direction_sim = treeFunction(['sphere_auxiliar_Link_BOTTOM.urdf'])
                elif simetry_activated and faceSet_Covered[cube][-1] == "TOP":
                    root_sim, direction_sim = treeFunction(['sphere_auxiliar_Link_TOP.urdf'])
                elif simetry_activated and faceSet_Covered[cube][-1] == "FRONT":
                    root_sim, direction_sim = treeFunction(['sphere_auxiliar_Link_BACK.urdf'])


                robot = AuxiliarSphere(robot, node.parent.node_name, joint, sphere, root)
                joints = node.node_name.split(" ")
                root, direction = treeFunction([joints[-1] + ".urdf"])
                robot = JointRepresentation_conctLimb(robot, sphere.sphere_name, node.node_name, blackSphere,blackSphere.blackSphere_name,
                                                      faceSet_Covered.get(cube, [])[-1], joint, root, False)
                sphere.sphere_N += 1
                extra_sphere.Extra_N += 1

                if simetry_activated:
                    if (z_axis.__contains__(node.parent.node_name) or x_axis.__contains__(node.parent.node_name) ):
                        symmetry_part = AuxiliarSphere(symmetry_part, node.parent.node_name, joint, sphere, root_sim)
                        joints = node.node_name.split(" ")
                        root_sim, direction = treeFunction([joints[-1] + ".urdf"])
                        symmetry_part = JointRepresentation_conctLimb(symmetry_part, sphere.sphere_name,
                                                                      f"{node.node_name}_sim", blackSphere,
                                                                      f"{blackSphere.blackSphere_name}_sim",
                                                                      faceSet_Covered.get(cube, [])[-1], joint,
                                                                      root_sim, True)
                        sphere.sphere_N += 1
                    else:
                        symmetry_part = AuxiliarSphere(symmetry_part, f"{node.parent.node_name}_sim", joint, sphere, root_sim)
                        joints = node.node_name.split(" ")
                        root_sim, direction = treeFunction([joints[-1] + ".urdf"])
                        symmetry_part = JointRepresentation_conctLimb(symmetry_part, sphere.sphere_name, f"{node.node_name}_sim", blackSphere, f"{blackSphere.blackSphere_name}_sim",
                                                              faceSet_Covered.get(cube, [])[-1], joint, root_sim, True)
                        sphere.sphere_N += 1

            else:
                joints = node.node_name.split(" ")
                root, direction = treeFunction([joints[-1] + ".urdf"])

                if node.parent.node_name.__contains__("wheel"):
                    robot = JointRepresentation_conctLimb(robot, node.parent.node_name, node.node_name, blackSphere,blackSphere.blackSphere_name, "",
                                                          joint, root, False)
                else:
                    robot = JointRepresentation_conctLimb(robot, extra_sphere.extraSphere_name, node.node_name,
                                                          blackSphere,blackSphere.blackSphere_name, "", joint, root, False)


                if simetry_activated:
                    root_sim, direction = treeFunction([joints[-1] + ".urdf"])
                    if node.parent.node_name.__contains__("wheel"):
                        symmetry_part = JointRepresentation_conctLimb(symmetry_part, f"{node.parent.node_name}_sim", f"{node.node_name}_sim", blackSphere,f"{blackSphere.blackSphere_name}_sim",
                                                              "", joint, root_sim, True)
                    else:
                        symmetry_part = JointRepresentation_conctLimb(symmetry_part, f"{extra_sphere.extraSphere_name}_sim", f"{node.node_name}_sim",
                                                              blackSphere,f"{blackSphere.blackSphere_name}_sim", "", joint, root_sim, True)
                extra_sphere.Extra_N += 1

        ## HERE IS THE LIMB CONSTRUCTION
        elif node.node_name.__contains__("limb_"):
            limb = node.node_name.split(" ")
            root, direction = treeFunction([limb[-1] + ".urdf"])

            if simetry_activated:

                robot = limbs(robot, blackSphere, blackSphere.blackSphere_name, node.node_name, extra_sphere, extra_sphere.extraSphere_name, joint,
                              root)
                blackSphere.blackSphere_N -= 1
                limb = node.node_name.split(" ")
                root_sim, direction = treeFunction([limb[-1] + ".urdf"])
                symmetry_part = limbs(symmetry_part, blackSphere, f"{blackSphere.blackSphere_name}_sim", f"{node.node_name}_sim", extra_sphere,
                                      f"{extra_sphere.extraSphere_name}_sim", joint, root_sim)
                save_file(symmetry_part, "symmetry.urdf")
                blackSphere.blackSphere_N += 1
            else:
                robot = limbs(robot, blackSphere, blackSphere.blackSphere_name, node.node_name, extra_sphere,extra_sphere.extraSphere_name, joint,
                              root)



        elif node.node_name.__contains__("wheel"):
            limb = node.node_name.split(" ")
            root, direction = treeFunction([limb[-1] + ".urdf"])
            robot = limbs(robot, blackSphere,blackSphere.blackSphere_name, node.node_name, extra_sphere, extra_sphere.extraSphere_name, joint, root)

            if simetry_activated:
                blackSphere.blackSphere_N -= 1
                limb = node.node_name.split(" ")
                root_sim, direction = treeFunction([limb[-1] + ".urdf"])
                symmetry_part = limbs(symmetry_part, blackSphere,f"{blackSphere.blackSphere_name}_sim", f"{node.node_name}_sim", extra_sphere, f"{extra_sphere.extraSphere_name}_sim", joint, root_sim)
                blackSphere.blackSphere_N += 1


        elif node.node_name.__contains__("ε") and node.parent.node_name == "0 body_Link_CUBE":
            cube = node.parent.node_name
            root, direction = treeFunction(input_file_sphereAUX)
            while True:
                if direction.split(".urdf")[0] in faceSet_Covered.get(cube, []):
                    root, direction = treeFunction(input_file_sphereAUX)
                else:
                    faceSet_Covered[cube].append(direction.split(".urdf")[0])
                    direction_occupied = direction.split(".urdf")[0]
                    break

        if not node.node_name == "0 ROOT" and not node.node_name.__contains__("joint"):
            """ CHECK IF THERE ARE ANY COLISION BETWEEN """
            committed_path = "robots_test/robot_update_free_Colision.urdf"
            robot, collision_found, skip_until_depth,  = collision_test_and_commit(
                robot,
                testing_robot,
                committed_path,
                robot_number,
                node.depth,
            )
            if not node.node_name == "0 ROOT" and not node.node_name == "0 body_Link_CUBE" and not node.node_name.__contains__("ε"):
                sim_check = True

            """ CHECK IF THERE ARE ANY COLISION BETWEEN """


    if simetry_activated and turn_sim_off_node != 0:
        save_file(symmetry_part, "simetry.urdf")
        simetry_activated = False
        root, _ = treeFunction(["simetry.urdf"])
        for child in root:
            robot.append(child)
        robot, collision_found, skip_until_depth = collision_test_and_commit(
            robot,
            testing_robot,
            committed_path,
            robot_number,
            0,
        )

    tree = ET.ElementTree(robot)
    ET.indent(tree, space="\t")
    ET.indent(tree, space="  ", level=0)
    output_folder = "robots/"
    # Ensure the output folder exists
    os.makedirs(output_folder, exist_ok=True)

    # Full path to save
    output_file = os.path.join(output_folder, output_file)
    shutil.copyfile(committed_path, output_file)
    os.remove(committed_path)

    print(f"Done, robot {robot_number} constructed and ready to train")
    print("--------------------------------------------")

    return output_file