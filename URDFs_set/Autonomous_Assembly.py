import xml.etree.ElementTree as ET
from random import randrange


def modify_robot(input_file_body, input_file_limbs, input_file_limbs_joints, output_file):
    robot = ET.Element("robot", name="combined_robot")


    i = 0
    cube_name = ""


    tree = ET.parse(input_file_body[0])
    root = tree.getroot()
    for child in root:
        print("Nome do link do corpo: ", child.attrib["name"])
        child.attrib["name"] = "body_link_"+str(i)
        cube_name = child.attrib["name"]
        print("Nome do link do corpo: ", child.attrib["name"])
        robot.append(child)



    ## AQUI COMEÇA O LIMBS JOINTS
    tree = ET.parse(input_file_limbs_joints[0])
    root = tree.getroot()

    for child in root:
        print("Nome do link do corpo: ", child.attrib["name"])
        child.attrib["name"] = cube_name+str(i)
        print("Nome do link do corpo: ", child.attrib["name"])
        robot.append(child)

    ## AQUI COMEÇA O LIMBS
    tree = ET.parse(input_file_limbs[0])
    root = tree.getroot()

    for child in root:
        robot.append(child)


    # Save the modified URDF to a new file
    tree = ET.ElementTree(robot)
    ET.indent(tree, space="  ", level=0)
    tree.write(output_file, encoding="utf-8", xml_declaration=True)
    print("Done")



def main(i):


    input_file_body= ["body_Link_CUBE.urdf"]
    input_file_limbs= ["limb_Link.urdf"]
    input_file_limbs_joints= ["B_joint_fixed_BACK.urdf"]

    output_file = f"corrected_robot{i}.urdf"  # Modified URDF for each iteration
    modify_robot(input_file_body, input_file_limbs, input_file_limbs_joints, output_file)
    return output_file


if __name__ == "__main__":
    file = main(1)