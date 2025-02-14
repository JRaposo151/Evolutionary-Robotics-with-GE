import xml.etree.ElementTree as ET
from random import randrange


def modify_robot(input_file_body, input_file_sphereAUX, input_file_limbs, input_file_limbs_joints, output_file):
    robot = ET.Element("robot", name="combined_robot")

    body_N = 0
    sphere_N = 0
    BlackSphere_N = 0
    limbs_N = 0
    limbs_joints_N = 0
    cube_name = ""
    sphere_name = "back_sphere_" + str(sphere_N)
    limbs_BlackSphere_name = "blackSphere_" + str(BlackSphere_N)
    limbs_joints_name = "link_square_" + str(limbs_joints_N)
    limb = "limb_" + str(limbs_N)


    tree = ET.parse(input_file_body[0])
    root = tree.getroot()
    print("######### Features do CORPO a ser construido #########")
    for child in root:
        if child.tag == "link":
            print("Nome do link do corpo antes : ", child.attrib["name"])
            child.attrib["name"] = "body_link_"+str(body_N)
            body_N += 1
            cube_name = child.attrib["name"]
            print("Nome do link do corpo depois : ", child.attrib["name"])

        elif child.tag == "joint":
            for sub_child in child:
                if sub_child.tag == "child":
                    sub_child.attrib["link"] = sphere_name
        robot.append(child)


    ## AQUI COMEÇA A SPHERE AUXILIAR
    tree = ET.parse(input_file_sphereAUX[0])
    root = tree.getroot()
    print("######### Features da ESFERA AUXILIAR a ser construido #########")


    for child in root:
        for sub_child in child:
            if sub_child.tag == "parent":
                print("Nome do link do corpo pai antes: ", sub_child.attrib["link"])
                sub_child.attrib["link"] = cube_name
                print("Nome do link do corpo pai depois: ", sub_child.attrib["link"])
            elif sub_child.tag == "child":
                print("Nome do link do corpo filho antes: ", sub_child.attrib["link"])
                sub_child.attrib["link"] = sphere_name
                print("Nome do link do corpo filho depois: ", sub_child.attrib["link"])
        if child.tag == "link":
            print("Nome do link da esfera auxiliar antes: ", child.attrib["name"])
            child.attrib["name"] = sphere_name
            print("Nome do link da esfera auxiliar depois: ", child.attrib["name"])
            sphere_N += 1
        robot.append(child)

    ## AQUI COMEÇA O JOINTS
    tree = ET.parse(input_file_limbs_joints[0])
    root = tree.getroot()

    print("######### Features do JOINT FIXO a ser construido #########")


    for child in root:

        if child.tag == "joint" and child.attrib["name"] == "fixed_joint_":
            for sub_child in child:
                if sub_child.tag == "child":
                    print("Nome do limb do corpo como filho antes: ", sub_child.attrib["link"])
                    sub_child.attrib["link"] = limbs_BlackSphere_name
                    print("Nome do limb do corpo como filho depois: ", sub_child.attrib["link"])
                elif sub_child.tag == "parent":
                    print("Nome do joint fixo como pai: ", sub_child.attrib["link"])
                    sub_child.attrib["link"] = limbs_joints_name
                    print("Nome do joint fixo como pai: ", sub_child.attrib["link"])

        elif child.tag == "joint" and child.attrib["name"] == "fixed_joint":
            for sub_child in child:
                if sub_child.tag == "parent":
                    print("Nome do joint da esfera pai antes: ", sub_child.attrib["link"])
                    sub_child.attrib["link"] = sphere_name
                    print("Nome do joint da esfera pai depois: ", sub_child.attrib["link"])
                elif sub_child.tag == "child":
                    print("Nome do joint da esfera filho antes: ", sub_child.attrib["link"])
                    sub_child.attrib["link"] = limbs_joints_name
                    print("Nome do joint da esfera filho depois: ", sub_child.attrib["link"])

        elif child.tag == "link":
            print("Nome do link da joint auxiliar antes: ", child.attrib["name"])
            child.attrib["name"] = limbs_joints_name
            print("Nome do link da joint auxiliar depois: ", child.attrib["name"])

        robot.append(child)

    ## AQUI COMEÇA O LIMBS
    tree = ET.parse(input_file_limbs[0])
    root = tree.getroot()

    print("######### Features do LIMB a ser construido #########")


    for child in root:
        if child.tag == "link" and child.attrib["name"] == "":
            print("Nome do link da esfera no limb antes: ", child.attrib["name"])
            child.attrib["name"] = limbs_BlackSphere_name
            print("Nome do link da esfera no limb depois: ", child.attrib["name"])

        elif child.tag == "joint" and child.attrib["name"] == "fixed_joint_":
            for sub_child in child:
                if sub_child.tag == "parent":
                    print("Nome do link do limb pai antes: ", sub_child.attrib["link"])
                    sub_child.attrib["link"] = limbs_BlackSphere_name
                    print("Nome do link do limb pai depois: ", sub_child.attrib["link"])
                    BlackSphere_N += 1

        robot.append(child)



    # Save the modified URDF to a new file
    tree = ET.ElementTree(robot)
    ET.indent(tree, space="  ", level=0)
    tree.write(output_file, encoding="utf-8", xml_declaration=True)
    print("Done")



def main(i):


    input_file_body= ["body_Link_CUBE.urdf"]
    input_file_sphereAUX = ["sphere_auxiliar_Link_BACK.urdf"]
    input_file_limbs= ["limb_Link.urdf"]
    input_file_limbs_joints= ["L_joint_fixed.urdf"]

    output_file = f"corrected_robot{i}.urdf"  # Modified URDF for each iteration
    modify_robot(input_file_body, input_file_sphereAUX, input_file_limbs, input_file_limbs_joints, output_file)
    return output_file


if __name__ == "__main__":
    file = main(1)