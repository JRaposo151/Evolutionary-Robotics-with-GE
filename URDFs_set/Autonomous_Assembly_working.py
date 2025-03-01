import random
import xml.etree.ElementTree as ET
from bigtree import preorder_iter


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



def treeFunction(file):
    piece_choice = random.choice(file)
    tree = ET.parse(piece_choice)
    root = tree.getroot()
    direction = [piece_choice.split("_")[-1]]
    return root, direction[0]


def body(robot, cube_name, root):
    for child in root:
        if child.tag == "link":
            child.attrib["name"] = cube_name
        robot.append(child)
    return robot

def AuxiliarSphere(robot, cube_name, sphere, root):
    for child in root:
        if child.tag == "link":
            child.attrib["name"] = sphere.sphere_name


        elif child.attrib["name"] == "joint_1":
            for sub_child in child:
                if sub_child.tag == "parent":
                    sub_child.attrib["link"] = cube_name
                elif sub_child.tag == "child":
                    sub_child.attrib["link"] = sphere.sphere_name


        robot.append(child)
    return robot


def JointRepresentation_conctBody(robot, sphere, representative_Joint, next_cube, root):
    for child in root:

        if child.tag == "joint" and child.attrib["name"] == "joint_1":
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
                for sub_child in child:
                    if sub_child.tag == "child":
                        sub_child.attrib["link"] = sphere.sphere_name
                    elif sub_child.tag == "parent":
                        sub_child.attrib["link"] = representative_Joint


            elif child.tag == "joint" and child.attrib["name"] == "joint_3":
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
                for sub_child in child:
                    if sub_child.tag == "child":
                        sub_child.attrib["link"] = next_cube
                    elif sub_child.tag == "parent":
                        sub_child.attrib["link"] = representative_Joint
        robot.append(child)
    return robot

def JointRepresentation_conctLimb(robot, sphere, representative_Joint, blackSphere, faceSet_Covered, root):
    for child in root:

        if child.tag == "joint" and child.attrib["name"] == "joint_1":
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

                elif sub_child.tag == "origin" and root.attrib["name"] == "L_JOINT_CONT_HZ":
                    if faceSet_Covered == "BACK":
                        sub_child.attrib["rpy"] = "1.55 0 0"
                        sub_child.attrib["xyz"] = "0 -0.03 0"
                    if faceSet_Covered == "FRONT":
                        sub_child.attrib["rpy"] = "-1.55 0 0"
                        sub_child.attrib["xyz"] = "0 0.03 0"
                    if faceSet_Covered == "TOP":
                        sub_child.attrib["xyz"] = "0 0 0.03"
                    if faceSet_Covered == "BOTTOM":
                        sub_child.attrib["rpy"] = "3.15 0 0"
                        sub_child.attrib["xyz"] = "0 0 -0.03 "
                    if faceSet_Covered == "RIGHT":
                        sub_child.attrib["rpy"] = "0 1.55 0"
                        sub_child.attrib["xyz"] = "0.03 0 0"
                    if faceSet_Covered == "LEFT":
                        sub_child.attrib["rpy"] = "0 -1.55 0"
                        sub_child.attrib["xyz"] = "-0.03 0 0"



                elif faceSet_Covered == "BACK":
                    sub_child.attrib["rpy"] = "1.55 0 0"
                elif faceSet_Covered == "FRONT":
                    sub_child.attrib["rpy"] = "-1.55 0 0"
                elif faceSet_Covered == "LEFT":
                    sub_child.attrib["rpy"] = "0 -1.55 0"
                elif faceSet_Covered == "RIGHT":
                    sub_child.attrib["rpy"] = "0 1.55 0"
                elif faceSet_Covered == "BOTTOM":
                    sub_child.attrib["rpy"] = "0 3.15 0"


        elif child.tag == "joint" and child.attrib["name"] == "joint_2":
            for sub_child in child:
                if sub_child.tag == "child":
                    sub_child.attrib["link"] = blackSphere.blackSphere_name
                elif sub_child.tag == "parent":
                    sub_child.attrib["link"] = representative_Joint

                elif sub_child.tag == "origin" and root.attrib["name"] == "L_JOINT_REVO": # TODO VER SE ISTO É REVO ou CONTINUOUS
                    if faceSet_Covered == "RIGHT":
                        sub_child.attrib["rpy"] = "0 1.6 0"
                    elif faceSet_Covered == "LEFT" or faceSet_Covered == "TOP" or faceSet_Covered == "BOTTOM":
                        sub_child.attrib["rpy"] = "0 -1.6 0"
                    elif faceSet_Covered == "FRONT":
                        sub_child.attrib["rpy"] = "-1.6 0 0"
                    elif faceSet_Covered == "BACK":
                        sub_child.attrib["rpy"] = "1.6 0 0"

        elif child.tag == "link":
            child.attrib["name"] = representative_Joint

        robot.append(child)
    return robot



def limbs(robot, blackSphere, limb, extra_sphere, root):
    for child in root:

        if child.tag == "link" and child.attrib["name"] == "":
            child.attrib["name"] = blackSphere.blackSphere_name

        elif child.tag == "joint" and child.attrib["name"] == "joint_1":
            for sub_child in child:
                if sub_child.tag == "parent":
                    sub_child.attrib["link"] = blackSphere.blackSphere_name
                    blackSphere.blackSphere_N += 1
                if sub_child.tag == "child":
                    sub_child.attrib["link"] = limb

        elif child.tag == "link" and child.attrib["name"] == "limb_link":
            child.attrib["name"] = limb

        elif child.tag == "joint" and child.attrib["name"] == "joint_2":
            for sub_child in child:
                if sub_child.tag == "parent":
                    sub_child.attrib["link"] = limb
                if sub_child.tag == "child":
                    sub_child.attrib["link"] = extra_sphere.extraSphere_name

        elif child.tag == "link" and (child.attrib["name"] == "limb_small_link_robot" or "limb_joint_bottom_blue_link"):
            child.attrib["name"] = extra_sphere.extraSphere_name

        robot.append(child)
    return robot



def assemblement(robot_tree, robot_number):


    input_file_body = ["URDFs_set/body_Link_CUBE.urdf"]

    input_file_sphereAUX = [
        "URDFs_set/sphere_auxiliar_Link_BACK.urdf", "URDFs_set/sphere_auxiliar_Link_BOTTOM.urdf",
        "URDFs_set/sphere_auxiliar_Link_FRONT.urdf", "URDFs_set/sphere_auxiliar_Link_LEFT.urdf",
        "URDFs_set/sphere_auxiliar_Link_RIGHT.urdf", "URDFs_set/sphere_auxiliar_Link_TOP.urdf"
    ]

    faceSet_Covered = {}
    sphere = SphereCounter()
    blackSphere = Limb_BlackSphereCounter()
    extra_sphere = Extra_SphereCounter()
    direction_occupied = ""

    print("Assembling Started: ")

    # Robot file creation
    print(f"Robot number: {robot_number} being assembled...")
    robot = ET.Element("robot", name=f"combined_robot{robot_number}")

    for node in preorder_iter(robot_tree):
        # for each node in the tree, it will be add to the robot file a component
        output_file = f"corrected_robot{robot_number}.urdf"  # Modified URDF for each iteration

        ## HERE IS THE BODY CONSTRUCTION
        if node.node_name.__contains__("body_Link_CUBE"):
            root, direction = treeFunction(input_file_body)  # in this case, the direction doesn t matter
            robot = body(robot, node.node_name, root)
            faceSet_Covered[node.node_name] = []
            if node.parent.node_name.__contains__("B_joint"):
                cube = node.node_name
                if direction_occupied == "LEFT":
                    faceSet_Covered[cube].append("RIGHT")
                if direction_occupied == "RIGHT":
                    faceSet_Covered[cube].append("LEFT")
                if direction_occupied == "TOP":
                    faceSet_Covered[cube].append("BOTTOM")
                if direction_occupied == "FRONT":
                    faceSet_Covered[cube].append("BACK")
                if direction_occupied == "BACK":
                    faceSet_Covered[cube].append("FRONT")
                if direction_occupied == "BOTTOM":
                    faceSet_Covered[cube].append("TOP")


        ## HERE IS THE AUXILIAR SPHERE CONSTRUCTION AND JOINT FOR BODY
        elif node.node_name.__contains__("B_joint"):
            cube = node.parent.node_name
            root, direction = treeFunction(input_file_sphereAUX)
            while True:
                if direction.split(".urdf")[0] in faceSet_Covered.get(cube, []):
                    root, direction = treeFunction(input_file_sphereAUX)
                else:
                    faceSet_Covered[cube].append(direction.split(".urdf")[0])
                    direction_occupied = direction.split(".urdf")[0]
                    break
            robot = AuxiliarSphere(robot, node.parent.node_name, sphere, root)
            # joint for the body
            joint = node.node_name.split(" ")
            root, direction = treeFunction(["URDFs_set/" + joint[-1] + "_" + direction])
            for child in node.children:
                robot = JointRepresentation_conctBody(robot, sphere, node.node_name, child.node_name, root)

        ## HERE IS THE LIMB JOINT CONSTRUCTION
        elif node.node_name.__contains__("L_joint"):
            cube = node.parent.node_name
            if node.parent.node_name.__contains__("body_Link_CUBE"):
                root, direction = treeFunction(input_file_sphereAUX)
                while True:
                    if direction.split(".urdf")[0] in faceSet_Covered.get(cube, []):
                        root, direction = treeFunction(input_file_sphereAUX)
                    else:
                        faceSet_Covered[cube].append(direction.split(".urdf")[0])
                        break
                robot = AuxiliarSphere(robot, node.parent.node_name, sphere, root)
                joint = node.node_name.split(" ")
                root, direction = treeFunction(["URDFs_set/" + joint[-1] + ".urdf"])
                robot = JointRepresentation_conctLimb(robot, sphere.sphere_name, node.node_name, blackSphere, faceSet_Covered.get(cube, [])[-1], root)
                sphere.sphere_N += 1
                extra_sphere.Extra_N += 1

            else:
                joint = node.node_name.split(" ")
                root, direction = treeFunction(["URDFs_set/" + joint[-1] + ".urdf"])

                if node.parent.node_name.__contains__("wheel"):
                    robot = JointRepresentation_conctLimb(robot, node.parent.node_name, node.node_name, blackSphere, "", root)
                else:
                    robot = JointRepresentation_conctLimb(robot, extra_sphere.extraSphere_name, node.node_name, blackSphere, "", root)
                extra_sphere.Extra_N += 1

        ## HERE IS THE LIMB CONSTRUCTION
        elif node.node_name.__contains__("limb_"):
            limb = node.node_name.split(" ")
            root, direction = treeFunction(["URDFs_set/" + limb[-1] + ".urdf"])
            robot = limbs(robot, blackSphere, node.node_name, extra_sphere, root)


        elif node.node_name.__contains__("wheel"):
            limb = node.node_name.split(" ")
            root, direction = treeFunction(["URDFs_set/" + limb[-1] + ".urdf"])
            robot = limbs(robot, blackSphere, node.node_name, extra_sphere, root)

    # Save the modified URDF to a new file
    tree = ET.ElementTree(robot)
    ET.indent(tree, space="\t")
    ET.indent(tree, space="  ", level=0)
    tree.write(output_file, encoding="utf-8", xml_declaration=True)
    print(f"Done, robot {robot_number} constructed and ready to train")
    print("--------------------------------------------")

    return output_file
