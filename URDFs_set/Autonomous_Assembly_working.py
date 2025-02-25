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
            child.attrib["name"] = cube_name
            print("Nome do link do corpo depois : ", child.attrib["name"])
        robot.append(child)
    return robot

def AuxiliarSphere(robot, cube_name, sphere, root):
    for child in root:
        print(child.attrib["name"])
        if child.tag == "link":
            print("Nome do link da esfera auxiliar antes: ", child.attrib["name"])
            child.attrib["name"] = sphere.sphere_name
            print("Nome do link da esfera auxiliar depois: ", child.attrib["name"])


        elif child.attrib["name"] == "joint_1":
            for sub_child in child:
                if sub_child.tag == "parent":
                    print("Nome do link do corpo pai antes: ", sub_child.attrib["link"])
                    sub_child.attrib["link"] = cube_name
                    print("Nome do link do corpo pai depois: ", sub_child.attrib["link"])
                elif sub_child.tag == "child":
                    print("Nome do link do corpo filho antes: ", sub_child.attrib["link"])
                    sub_child.attrib["link"] = sphere.sphere_name
                    print("Nome do link do corpo filho depois: ", sub_child.attrib["link"])

        # else:
        #     for sub_child in child:
        #         if sub_child.tag == "parent":
        #             print("Nome do link do corpo pai antes: ", sub_child.attrib["link"])
        #             sub_child.attrib["link"] = sphere.sphere_name
        #             print("Nome do link do corpo pai depois: ", sub_child.attrib["link"])
        #             sphere.sphere_N += 1
        #         elif sub_child.tag == "child":
        #             print("Nome do link do corpo filho antes: ", sub_child.attrib["link"])
        #             sub_child.attrib["link"] = link_auxiliar
        #             print("Nome do link do corpo filho depois: ", sub_child.attrib["link"])


        robot.append(child)
    return robot


def JointRepresentation_conctBody(robot, sphere, representative_Joint, next_cube, root):
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
                    sub_child.attrib["link"] = representative_Joint
                    print("Nome do joint da esfera filho depois: ", sub_child.attrib["link"])
                else:
                    break

        if root.attrib["name"] == "B_JOINT_REVO":
            if child.tag == "link":
                if child.attrib["name"] == "extra_sphere":
                    print("Nome do link da esfera extra antes: ", child.attrib["name"])
                    child.attrib["name"] = sphere.sphere_name
                    print("Nome do link da esfera extra depois: ", child.attrib["name"])
                else:
                    print("Nome do link da joint auxiliar antes: ", child.attrib["name"])
                    child.attrib["name"] = representative_Joint
                    print("Nome do link da joint auxiliar depois: ", child.attrib["name"])


            if child.tag == "joint" and child.attrib["name"] == "joint_2":
                for sub_child in child:
                    if sub_child.tag == "child":
                        print("Nome do limb do corpo como filho antes: ", sub_child.attrib["link"])
                        sub_child.attrib["link"] = sphere.sphere_name
                        print("Nome do limb do corpo como filho depois: ", sub_child.attrib["link"])
                    elif sub_child.tag == "parent":
                        print("Nome do joint fixo como pai: ", sub_child.attrib["link"])
                        sub_child.attrib["link"] = representative_Joint
                        print("Nome do joint fixo como pai: ", sub_child.attrib["link"])


            elif child.tag == "joint" and child.attrib["name"] == "joint_3":
                for sub_child in child:
                    if sub_child.tag == "parent":
                        print("Nome do joint da esfera pai antes: ", sub_child.attrib["link"])
                        sub_child.attrib["link"] = sphere.sphere_name
                        sphere.sphere_N += 1
                        print("Nome do joint da esfera pai depois: ", sub_child.attrib["link"])
                    elif sub_child.tag == "child":
                        print("Nome do joint da esfera filho antes: ", sub_child.attrib["link"])
                        sub_child.attrib["link"] = next_cube
                        print("Nome do joint da esfera filho depois: ", sub_child.attrib["link"])




        elif child.tag == "link":
            if child.attrib["name"]:
                print("Nome do link da joint auxiliar antes: ", child.attrib["name"])
                child.attrib["name"] = representative_Joint
                print("Nome do link da joint auxiliar depois: ", child.attrib["name"])
            # else:
            #     print("Nome do link da joint auxiliar antes: ", child.attrib["name"])
            #     child.attrib["name"] = extra_sphere.extraSphere_name
            #     print("Nome do link da joint auxiliar depois: ", child.attrib["name"])

        elif child.tag == "joint" and child.attrib["name"] == "joint_2":
                for sub_child in child:
                    if sub_child.tag == "child":
                        print("Nome do limb do corpo como filho antes: ", sub_child.attrib["link"])
                        sub_child.attrib["link"] = next_cube
                        print("Nome do limb do corpo como filho depois: ", sub_child.attrib["link"])
                    elif sub_child.tag == "parent":
                        print("Nome do joint fixo como pai: ", sub_child.attrib["link"])
                        sub_child.attrib["link"] = representative_Joint
                        print("Nome do joint fixo como pai: ", sub_child.attrib["link"])



        robot.append(child)
    return robot

def JointRepresentation_conctLimb(robot, sphere, representative_Joint, blackSphere, root):
    for child in root:

        if child.tag == "joint" and child.attrib["name"] == "joint_1":
            for sub_child in child:
                if sub_child.tag == "parent":
                    print("Nome do joint da esfera pai antes: ", sub_child.attrib["link"])
                    sub_child.attrib["link"] = sphere
                    print("Nome do joint da esfera pai depois: ", sub_child.attrib["link"])
                elif sub_child.tag == "child":
                    print("Nome do joint da esfera filho antes: ", sub_child.attrib["link"])
                    sub_child.attrib["link"] = representative_Joint
                    print("Nome do joint da esfera filho depois: ", sub_child.attrib["link"])

        elif child.tag == "joint" and child.attrib["name"] == "joint_2":
            for sub_child in child:
                if sub_child.tag == "child":
                    print("Nome do limb do corpo como filho antes: ", sub_child.attrib["link"])
                    sub_child.attrib["link"] = blackSphere.blackSphere_name
                    print("Nome do limb do corpo como filho depois: ", sub_child.attrib["link"])
                elif sub_child.tag == "parent":
                    print("Nome do joint fixo como pai: ", sub_child.attrib["link"])
                    sub_child.attrib["link"] = representative_Joint
                    print("Nome do joint fixo como pai: ", sub_child.attrib["link"])


        elif child.tag == "link":
            print("Nome do link da joint auxiliar antes: ", child.attrib["name"])
            child.attrib["name"] = representative_Joint
            print("Nome do link da joint auxiliar depois: ", child.attrib["name"])



        robot.append(child)
    return robot



def limbs(robot, blackSphere, limb, extra_sphere, root):
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
                    sub_child.attrib["link"] = limb

        elif child.tag == "link" and child.attrib["name"] == "limb_link":
            child.attrib["name"] = limb

        elif child.tag == "joint" and child.attrib["name"] == "joint_2":
            for sub_child in child:
                if sub_child.tag == "parent":
                    print("Nome do link do limb pai antes: ", sub_child.attrib["link"])
                    sub_child.attrib["link"] = limb
                    print("Nome do link do limb pai depois: ", sub_child.attrib["link"])
                if sub_child.tag == "child":
                    sub_child.attrib["link"] = extra_sphere.extraSphere_name

        elif child.tag == "link" and child.attrib["name"] == "limb_small_link_robot":
            child.attrib["name"] = extra_sphere.extraSphere_name


        robot.append(child)
    return robot



def assemblement(robot_tree, robot_number = 1):


    input_file_body = ["URDFs_set/body_Link_CUBE.urdf"]

    input_file_sphereAUX = [
        "URDFs_set/sphere_auxiliar_Link_BACK.urdf", "URDFs_set/sphere_auxiliar_Link_BOTTOM.urdf",
        "URDFs_set/sphere_auxiliar_Link_FRONT.urdf", "URDFs_set/sphere_auxiliar_Link_LEFT.urdf",
        "URDFs_set/sphere_auxiliar_Link_RIGHT.urdf", "URDFs_set/sphere_auxiliar_Link_TOP.urdf"
    ]

    faceSet_Covered = []
    sphere = SphereCounter()
    blackSphere = Limb_BlackSphereCounter()
    extra_sphere = Extra_SphereCounter()

    print("Assembling Started: ")
    for i in range(0, robot_number):
        # Robot file creation
        print(f"Robot number: {i} being assembled...")
        robot = ET.Element("robot", name=f"combined_robot{i}")

        for node in preorder_iter(robot_tree):
            # for each node in the tree, it will be add to the robot file a component
            output_file = f"corrected_robot{i}.urdf"  # Modified URDF for each iteration
            # TODO VERIFICAR SE
            # TODO DIREÇÃO tem de mudar

            if node.node_name.__contains__("ROOT") or node.node_name.__contains__("ε"):
                print(f"{node.node_name} Being ignored, nothing to be assembled.")

            ## HERE IS THE BODY CONSTRUCTION
            elif node.node_name.__contains__("body_Link_CUBE"):
                root, direction = treeFunction(input_file_body)  # in this case, the direction doesn t matter
                print("######### Features do CORPO a ser construido #########")
                robot = body(robot, node.node_name, root)

            ## HERE IS THE AUXILIAR SPHERE CONSTRUCTION AND JOINT FOR BODY
            elif node.node_name.__contains__("B_joint"):
                root, direction = treeFunction(input_file_sphereAUX)
                while True:
                    if direction in faceSet_Covered:
                        root, direction = treeFunction(input_file_sphereAUX)
                    faceSet_Covered.append(direction.split(".urdf")[0])
                    break
                print(f"######### Features da ESFERA AUXILIAR a ser construido na parte {faceSet_Covered[-1]} #########")
                print(node.parent.node_name)
                robot = AuxiliarSphere(robot, node.parent.node_name, sphere, root)

                # joint for the body
                joint = node.node_name.split(" ")
                root, direction = treeFunction(["URDFs_set/" + joint[-1] + "_" + direction])
                print(f"######### Features do URDFs_set/" + joint[-1] + "_" + direction + " a ser construido #########")

                for child in node.children:
                    robot = JointRepresentation_conctBody(robot, sphere, node.node_name, child.node_name, root)



            ## HERE IS THE LIMB JOINT CONSTRUCTION
            elif node.node_name.__contains__("L_joint"):
                if node.parent.node_name.__contains__("body_Link_CUBE"):
                    root, direction = treeFunction(input_file_sphereAUX)
                    while True:
                        if direction in faceSet_Covered:
                            root, direction = treeFunction(input_file_sphereAUX)
                        faceSet_Covered.append(direction.split(".urdf")[0])
                        break
                    print(f"######### Features da ESFERA AUXILIAR a ser construido na parte {faceSet_Covered[-1]} #########")
                    print(node.parent.node_name)
                    robot = AuxiliarSphere(robot, node.parent.node_name, sphere, root)

                    joint = node.node_name.split(" ")
                    root, direction = treeFunction(["URDFs_set/" + joint[-1] + ".urdf"])
                    print(f"######### Features do URDFs_set/" + joint[-1] + ".urdf" + " a ser construido #########")
                    for child in node.children:
                        robot = JointRepresentation_conctLimb(robot, sphere.sphere_name, node.node_name, blackSphere, root)
                        sphere.sphere_N +=1
                else:
                    joint = node.node_name.split(" ")
                    root, direction = treeFunction(["URDFs_set/" + joint[-1] + ".urdf"])
                    print(f"######### Features do URDFs_set/" + joint[-1] + ".urdf" + " a ser construido #########")
                    for child in node.children:
                        robot = JointRepresentation_conctLimb(robot, extra_sphere.extraSphere_name, node.node_name, blackSphere, root)
                        extra_sphere.Extra_N +=1




                ## HERE IS THE LIMB CONSTRUCTION
            elif node.node_name.__contains__("limb_"):
                limb = node.node_name.split(" ")
                root, direction = treeFunction(["URDFs_set/" + limb[-1] + ".urdf"])
                print(f"######### Features do URDFs_set/" + limb[-1] + ".urdf" + " a ser construido #########")
                robot = limbs(robot, blackSphere, node.node_name, extra_sphere, root)

            elif node.node_name.__contains__("wheel"):
                limb = node.node_name.split(" ")
                root, direction = treeFunction(["URDFs_set/" + limb[-1] + ".urdf"])
                print(f"######### Features do URDFs_set/" + limb[-1] + ".urdf" + " a ser construido #########")
                robot = limbs(robot, blackSphere, node.node_name, extra_sphere, root)



            print("--------------------------------------------")
            ET.dump(robot)
        # Save the modified URDF to a new file
        tree = ET.ElementTree(robot)
        ET.indent(tree, space="\t")
        ET.indent(tree, space="  ", level=0)
        tree.write(output_file, encoding="utf-8", xml_declaration=True)
        print(f"Done, robot {robot_number} constructed and ready to train")

    return output_file







































