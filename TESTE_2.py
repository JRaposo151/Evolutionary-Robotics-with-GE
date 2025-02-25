import random
import xml.etree.ElementTree as ET
from bigtree import preorder_iter


class SphereCounter:
    def __init__(self):
        self.sphere_N = 0  # Initial counter

    @property
    def sphere_name(self):
        return f"backSphere_{self.sphere_N}"  # Automatically updates


class BodyCounter:
    def __init__(self):
        self.body_N = 0  # Initial counter

    @property
    def body_name(self):
        return f"body_link_{self.body_N}"  # Automatically updates


class Limb_BlackSphereCounter:
    def __init__(self):
        self.blackSphere_N = 0  # Initial counter

    @property
    def blackSphere_name(self):
        return f"blackSphere_{self.blackSphere_N}"  # Automatically updates


class Representative_JointCounter:
    def __init__(self):
        self.representativeJoints_N = 0  # Initial counter

    @property
    def representativeJoint_name(self):
        return f"representativeJoint_{self.representativeJoints_N}"  # Automatically updates


class Limbs_Counter:
    def __init__(self):
        self.Limbs_N = 0  # Initial counter

    @property
    def limb_name(self):
        return f"Limb_{self.Limbs_N}"  # Automatically updates


class Extra_SphereCounter:
    def __init__(self):
        self.Extra_N = 0  # Initial counter

    @property
    def extraSphere_name(self):
        return f"extra_sphere_{self.Extra_N}"  # Automatically updates

#TODO CONSTRUIR AINDA CONDIÇÔES PARA SEGUIR O BACK; FRONT; ETC
def treeFunction(file):
    piece_choice = random.choice(file)
    tree = ET.parse(piece_choice)
    root = tree.getroot()
    print("----------------------------------------")
    ET.dump(root)
    print("----------------------------------------")
    direction = [piece_choice.split("_")[-1]]
    return root, direction[0]


def body(robot, cube_name, root):
    for child in root:
        if child.tag == "link":
            print("Nome do link do corpo antes : ", child.attrib["name"])
            child.attrib["name"] = cube_name.body_name
            print("Nome do link do corpo depois : ", child.attrib["name"])
        robot.append(child)
    return robot

def AuxiliarSphere(robot, cube_name, sphere, root):
    for child in root:

        if child.tag == "link":
            print("Nome do link da esfera auxiliar antes: ", child.attrib["name"])
            child.attrib["name"] = sphere.sphere_name
            print("Nome do link da esfera auxiliar depois: ", child.attrib["name"])
        else:
            for sub_child in child:
                if sub_child.tag == "parent":
                    print("Nome do link do corpo pai antes: ", sub_child.attrib["link"])
                    sub_child.attrib["link"] = cube_name.body_name
                    print("Nome do link do corpo pai depois: ", sub_child.attrib["link"])
                elif sub_child.tag == "child":
                    print("Nome do link do corpo filho antes: ", sub_child.attrib["link"])
                    sub_child.attrib["link"] = sphere.sphere_name
                    print("Nome do link do corpo filho depois: ", sub_child.attrib["link"])

        robot.append(child)
    return robot



def assemblement(
        input_file_body,
        input_file_sphereAUX,
        output_file,
        robot_node,
        robot_number,
        robot):

    sphere = SphereCounter()
    cube_name = BodyCounter()
    blackSphere = Limb_BlackSphereCounter()
    representative_Joint = Representative_JointCounter()
    limb = Limbs_Counter()
    extra_sphere = Extra_SphereCounter()
    faceSet_Covered = []

    if robot_node.node_name.__contains__("ROOT") or robot_node.node_name.__contains__("ε"):
        return None

    ## HERE IS THE BODY CONSTRUCTION
    if robot_node.node_name.__contains__("body_Link_CUBE"):
        root, direction = treeFunction(input_file_body)  # in this case, the direction doesn t matter
        print("######### Features do CORPO a ser construido #########")
        robot = body(robot, cube_name, root)
        return None

    ## HERE IS THE AUXILIAR SPHERE CONSTRUCTION and Joint for Body
    if robot_node.node_name.__contains__("B_joint"):
        root, direction = treeFunction(input_file_sphereAUX)
        while True:
            if direction in faceSet_Covered:
                root, direction = treeFunction(input_file_sphereAUX)
            faceSet_Covered.append(direction.split(".urdf")[0])
            break
        print("######### Features da ESFERA AUXILIAR a ser construido #########")
        robot = AuxiliarSphere(robot, cube_name, sphere, root)
        joint = robot_node.node_name.split(" ")
        print(joint[-1])
        print("URDFs_set/"+ joint[-1] + "_" + direction)
        root, direction = treeFunction(["URDFs_set/"+ joint[-1] + "_" + direction])
        return None



def main(robot_tree, robot_number = 1):
    input_file_body = ["URDFs_set/body_Link_CUBE.urdf"]

    input_file_sphereAUX = [
        "URDFs_set/sphere_auxiliar_Link_BACK.urdf", "URDFs_set/sphere_auxiliar_Link_BOTTOM.urdf",
        "URDFs_set/sphere_auxiliar_Link_FRONT.urdf", "URDFs_set/sphere_auxiliar_Link_LEFT.urdf",
        "URDFs_set/sphere_auxiliar_Link_RIGHT.urdf", "URDFs_set/sphere_auxiliar_Link_TOP.urdf"
    ]

    print("Assembling...")
    for i in range(0, robot_number):
        # Robot file creation
        robot = ET.Element("robot", name=f"combined_robot{i}")
        ET.dump(robot)
        for node in preorder_iter(robot_tree):
            # for each node in the tree, it will be add to the robot file a component
            output_file = f"corrected_robot{i}.urdf"  # Modified URDF for each iteration
            assemblement(
                input_file_body,
                input_file_sphereAUX,
                output_file,
                node,
                i,
                robot
            )
            ET.dump(robot)
        # Save the modified URDF to a new file
        tree = ET.ElementTree(robot)
        ET.indent(tree, space="\t")
        ET.indent(tree, space="  ", level=0)
        tree.write(output_file, encoding="utf-8", xml_declaration=True)
        print(f"Done, robot {robot_number} constructed and ready to train")

        return output_file
