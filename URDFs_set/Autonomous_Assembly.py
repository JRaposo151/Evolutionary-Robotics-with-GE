import xml.etree.ElementTree as ET
from random import randrange


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

#TODO CONSTRUIR MAIS TARDE AQUI O FACTOR RANDOM PARA ESCOLHA E AINDA CONDIÇÔES PARA SEGUIR O BACK; FRONT; ETC
def treeFunction(file):
    tree = ET.parse(file[0])
    root = tree.getroot()
    return root


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
                    cube_name.body_N += 1
                    print("Nome do link do corpo pai depois: ", sub_child.attrib["link"])
                elif sub_child.tag == "child":
                    print("Nome do link do corpo filho antes: ", sub_child.attrib["link"])
                    sub_child.attrib["link"] = sphere.sphere_name
                    print("Nome do link do corpo filho depois: ", sub_child.attrib["link"])

        robot.append(child)
    return robot

def JointRepresentation(robot, sphere, blackSphere, representative_Joint, root):
    for child in root:

        if child.tag == "joint" and child.attrib["name"] == "joint_2":
            for sub_child in child:
                if sub_child.tag == "child":
                    print("Nome do limb do corpo como filho antes: ", sub_child.attrib["link"])
                    sub_child.attrib["link"] = blackSphere.blackSphere_name
                    print("Nome do limb do corpo como filho depois: ", sub_child.attrib["link"])
                elif sub_child.tag == "parent":
                    print("Nome do joint fixo como pai: ", sub_child.attrib["link"])
                    sub_child.attrib["link"] = representative_Joint.representativeJoint_name
                    print("Nome do joint fixo como pai: ", sub_child.attrib["link"])
                    representative_Joint.representativeJoints_N += 1

        elif child.tag == "joint" and child.attrib["name"] == "joint_1":
            for sub_child in child:
                if sub_child.tag == "parent":
                    print("Nome do joint da esfera pai antes: ", sub_child.attrib["link"])
                    sub_child.attrib["link"] = sphere.sphere_name
                    sphere.sphere_N += 1
                    print("Nome do joint da esfera pai depois: ", sub_child.attrib["link"])
                elif sub_child.tag == "child":
                    print("Nome do joint da esfera filho antes: ", sub_child.attrib["link"])
                    sub_child.attrib["link"] = representative_Joint.representativeJoint_name
                    print("Nome do joint da esfera filho depois: ", sub_child.attrib["link"])

        elif child.tag == "link":
            print("Nome do link da joint auxiliar antes: ", child.attrib["name"])
            child.attrib["name"] = representative_Joint.representativeJoint_name
            print("Nome do link da joint auxiliar depois: ", child.attrib["name"])

        robot.append(child)
    return robot

def limbs(robot, blackSphere, root):
    for child in root:
        if child.tag == "link" and child.attrib["name"] == "":
            print("Nome do link da esfera no limb antes: ", child.attrib["name"])
            child.attrib["name"] = blackSphere.blackSphere_name
            print("Nome do link da esfera no limb depois: ", child.attrib["name"])

        elif child.tag == "joint" and child.attrib["name"] == "joint_1":
            for sub_child in child:
                if sub_child.tag == "parent":
                    print("Nome do link do limb pai antes: ", sub_child.attrib["link"])
                    sub_child.attrib["link"] = blackSphere.blackSphere_name
                    print("Nome do link do limb pai depois: ", sub_child.attrib["link"])
                    blackSphere.blackSphere_N += 1

        robot.append(child)
    return robot



def assemblement(input_file_body, input_file_sphereAUX, input_file_limbs, input_file_limbs_joints, output_file):

    robot = ET.Element("robot", name="combined_robot")
    sphere = SphereCounter()
    cube_name = BodyCounter()
    blackSphere = Limb_BlackSphereCounter()
    representative_Joint = Representative_JointCounter()
    Limb = Limbs_Counter()

    ## HERE IS THE BODY CONSTRUCTION
    root = treeFunction(input_file_body)
    print("######### Features do CORPO a ser construido #########")
    robot = body(robot, cube_name,  root)

    ## HERE IS THE AUXILIAR SPHERE CONSTRUCTION
    root = treeFunction(input_file_sphereAUX)
    print("######### Features da ESFERA AUXILIAR a ser construido #########")
    robot = AuxiliarSphere(robot, cube_name, sphere, root)

    ## HERE IS THE JOINT CONSTRUCTION
    root = treeFunction(input_file_limbs_joints)
    print("######### Features do JOINT FIXO a ser construido #########")
    robot = JointRepresentation(robot, sphere, blackSphere, representative_Joint, root)

    ## HERE IS THE LIMB CONSTRUCTION
    root = treeFunction(input_file_limbs)
    print("######### Features do LIMB a ser construido #########")
    robot = limbs(robot, blackSphere, root)

    # Save the modified URDF to a new file
    tree = ET.ElementTree(robot)
    ET.indent(tree, space="  ", level=0)
    tree.write(output_file, encoding="utf-8", xml_declaration=True)
    print("Done")


def main(i):
    input_file_body = ["body_Link_CUBE.urdf"]
    input_file_sphereAUX = ["sphere_auxiliar_Link_BACK.urdf"]
    input_file_limbs = ["limb_Link.urdf"]
    input_file_limbs_joints = ["B_joint_fixed_BACK.urdf"]

    output_file = f"corrected_robot{i}.urdf"  # Modified URDF for each iteration
    assemblement(input_file_body, input_file_sphereAUX, input_file_limbs, input_file_limbs_joints, output_file)
    return output_file


if __name__ == "__main__":
    file = main(1)