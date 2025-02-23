import random
import xml.etree.ElementTree as ET


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

def JointRepresentation_conctLimb(robot, sphere, blackSphere, representative_Joint, root):
    for child in root:

        if child.tag == "joint" and child.attrib["name"] == "joint_1":
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

        elif child.tag == "joint" and child.attrib["name"] == "joint_2":
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

        elif child.tag == "link":
            print("Nome do link da joint auxiliar antes: ", child.attrib["name"])
            child.attrib["name"] = representative_Joint.representativeJoint_name
            print("Nome do link da joint auxiliar depois: ", child.attrib["name"])

        robot.append(child)
    return robot


def JointRepresentation_conctBody(robot, sphere, representative_Joint, extra_sphere, root):
    for child in root:

        if child.tag == "joint" and child.attrib["name"] == "joint_1":
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

        if root.attrib["name"] == "B_JOINT_REVO":
            if child.tag == "joint" and child.attrib["name"] == "joint_2":
                for sub_child in child:
                    if sub_child.tag == "child":
                        print("Nome do limb do corpo como filho antes: ", sub_child.attrib["link"])
                        sub_child.attrib["link"] = extra_sphere.extraSphere_name
                        print("Nome do limb do corpo como filho depois: ", sub_child.attrib["link"])
                    elif sub_child.tag == "parent":
                        print("Nome do joint fixo como pai: ", sub_child.attrib["link"])
                        sub_child.attrib["link"] = representative_Joint.representativeJoint_name
                        print("Nome do joint fixo como pai: ", sub_child.attrib["link"])
                        representative_Joint.representativeJoints_N += 1

            elif child.tag == "joint" and child.attrib["name"] == "joint_3":
                for sub_child in child:
                    if sub_child.tag == "parent":
                        print("Nome do joint da esfera pai antes: ", sub_child.attrib["link"])
                        sub_child.attrib["link"] = extra_sphere.extraSphere_name
                        extra_sphere.Extra_N +=1
                        print("Nome do joint da esfera pai depois: ", sub_child.attrib["link"])
                    elif sub_child.tag == "child":
                        print("Nome do joint da esfera filho antes: ", sub_child.attrib["link"])
                        sub_child.attrib["link"] = ""#TODO nome do proximo body
                        print("Nome do joint da esfera filho depois: ", sub_child.attrib["link"])

        elif child.tag == "link":
            if child.attrib["name"] == "auxiliar":
                print("Nome do link da joint auxiliar antes: ", child.attrib["name"])
                child.attrib["name"] = representative_Joint.representativeJoint_name
                print("Nome do link da joint auxiliar depois: ", child.attrib["name"])
            else:
                print("Nome do link da joint auxiliar antes: ", child.attrib["name"])
                child.attrib["name"] = extra_sphere.extraSphere_name
                print("Nome do link da joint auxiliar depois: ", child.attrib["name"])

        else:
            if child.tag == "joint" and child.attrib["name"] == "joint_2":
                for sub_child in child:
                    if sub_child.tag == "child":
                        print("Nome do limb do corpo como filho antes: ", sub_child.attrib["link"])
                        sub_child.attrib["link"] = ""#TODO nome do proximo body
                        print("Nome do limb do corpo como filho depois: ", sub_child.attrib["link"])
                    elif sub_child.tag == "parent":
                        print("Nome do joint fixo como pai: ", sub_child.attrib["link"])
                        sub_child.attrib["link"] = representative_Joint.representativeJoint_name
                        print("Nome do joint fixo como pai: ", sub_child.attrib["link"])
                        representative_Joint.representativeJoints_N += 1

        robot.append(child)
    return robot

def limbs(robot, blackSphere, limb, root):
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
                if sub_child.tag == "child":
                    sub_child.attrib["link"] = limb.limbSphere_name
        elif child.tag == "link" and child.attrib["name"] == "limb_link":
            child.attrib["name"] = limb.limbSphere_name

        elif child.tag == "joint" and child.attrib["name"] == "joint_2":
            for sub_child in child:
                if sub_child.tag == "parent":
                    print("Nome do link do limb pai antes: ", sub_child.attrib["link"])
                    sub_child.attrib["link"] = limb.limbSphere_name
                    print("Nome do link do limb pai depois: ", sub_child.attrib["link"])
                    limb.Limbs_N += 1
                if sub_child.tag == "child":
                    sub_child.attrib["link"] = limb.limbSphere_name
        elif child.tag == "link" and child.attrib["name"] == "limb_small_link_robot":
            child.attrib["name"] = limb.limbSphere_name


        robot.append(child)
    return robot



def assemblement(
        input_file_body,
        input_file_sphereAUX,
        output_file,
        robot_prototype,
        robot_number):

    robot = ET.Element("robot", name="combined_robot")
    sphere = SphereCounter()
    cube_name = BodyCounter()
    blackSphere = Limb_BlackSphereCounter()
    representative_Joint = Representative_JointCounter()
    limb = Limbs_Counter()
    extra_sphere = Extra_SphereCounter()
    faceSet_Covered = []

    for buildingBlock in robot_prototype.split():
        ## HERE IS THE BODY CONSTRUCTION
        if buildingBlock == "body_Link_CUBE":
            cube_name.body_N += 1 # TODO corrigir aqui pois nao posso acrecentar mais um no nome aqui, porque apos os 6 proximos facesets, o numero tem de voltar ao anterior
            root, direction = treeFunction(input_file_body) # in this case, the direction doesn t matter
            print("######### Features do CORPO a ser construido #########")
            robot = body(robot, cube_name, root)

        ## HERE IS THE AUXILIAR SPHERE CONSTRUCTION
        elif buildingBlock == "FaceSet:":
            root, direction = treeFunction(input_file_sphereAUX)
            while direction in faceSet_Covered:
                faceSet_Covered.append(direction.split(".urdf")[0])
            print("######### Features da ESFERA AUXILIAR a ser construido #########")
            robot = AuxiliarSphere(robot, cube_name, sphere, root)

        ## HERE IS THE BODY JOINT CONSTRUCTION
        elif ("B_joint") in buildingBlock:
            root, direction = treeFunction("URDFs_set/" + buildingBlock + direction)
            print(f"######### Features do {buildingBlock} a ser construido #########")
            robot = JointRepresentation_conctBody(robot, sphere, representative_Joint, extra_sphere, root)
            #TODO muito provalvelmente chamada recursiva aqui para construção de diversos corpos

        ## HERE IS THE LIMB JOINT CONSTRUCTION
        elif ("L_joint") in buildingBlock:
            root = treeFunction("URDFs_set/" + buildingBlock + ".urdf")
            print(f"######### Features do {buildingBlock} a ser construido #########")
            robot = JointRepresentation_conctLimb(robot, sphere, blackSphere, representative_Joint, root)

        ## HERE IS THE LIMB CONSTRUCTION
        elif ("limb_" or "wheel") in buildingBlock:
            root = treeFunction("" + buildingBlock + ".urdf")
            print("######### Features do LIMB a ser construido #########")
            robot = limbs(robot, blackSphere, limb, root)

    # Save the modified URDF to a new file
    tree = ET.ElementTree(robot)
    ET.indent(tree, space="  ", level=0)
    tree.write(output_file, encoding="utf-8", xml_declaration=True)
    print(f"Done, robot {robot_number} constructed and ready to train")


def main(robot_prototype, robot_number = 1):
    input_file_body = ["URDFs_set/body_Link_CUBE.urdf"]

    input_file_sphereAUX = [
        "URDFs_set/sphere_auxiliar_Link_BACK.urdf", "URDFs_set/sphere_auxiliar_Link_BOTTOM.urdf",
        "URDFs_set/sphere_auxiliar_Link_FRONT.urdf", "URDFs_set/sphere_auxiliar_Link_LEFT.urdf",
        "URDFs_set/sphere_auxiliar_Link_RIGHT.urdf", "URDFs_set/sphere_auxiliar_Link_TOP.urdf"
    ]

    for i in range(0, robot_number):
        output_file = f"corrected_robot{i}.urdf"  # Modified URDF for each iteration
        assemblement(
            input_file_body,
            input_file_sphereAUX,
            output_file,
            robot_prototype,
            i
        )
        return output_file
