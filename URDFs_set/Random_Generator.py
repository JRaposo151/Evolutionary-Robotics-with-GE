import xml.etree.ElementTree as ET
from random import randrange


def modify_robot(input_file_body, input_file_limbs, input_file_limbs_joints, output_file):
    robot = ET.Element("robot", name="combined_robot")

    aux = randrange(0, 2)
    print(aux)
    tree = ET.parse(input_file_body[aux])
    root = tree.getroot()

    for child in root:
        robot.append(child)


    ## AQUI COMEÇA O LIMBS JOINTS
    aux = randrange(0, 3)
    print(aux)
    tree = ET.parse(input_file_limbs_joints[aux])
    root = tree.getroot()

    for child in root:
        robot.append(child)

    ## AQUI COMEÇA O LIMBS
    aux = randrange(0, 6)
    print(aux)
    tree = ET.parse(input_file_limbs[aux])
    root = tree.getroot()

    for child in root:
        robot.append(child)


    # Save the modified URDF to a new file
    tree = ET.ElementTree(robot)
    ET.indent(tree, space="  ", level=0)
    tree.write(output_file, encoding="utf-8", xml_declaration=True)
    print("Done")



def main(i):


    input_file_body= ["URDFs_set/body_Link.urdf", "URDFs_set/body_Link_amarelo.urdf", "URDFs_set/body_Link_verde.urdf"]
    input_file_limbs= ["URDFs_set/limb_Link.urdf", "URDFs_set/limb_Link_amarelo.urdf","URDFs_set/limb_Link_preto.urdf", "URDFs_set/limb_Link_verde.urdf", "URDFs_set/limb_Link_vermelho.urdf", "URDFs_set/limb_Link_rosa.urdf"]
    input_file_limbs_joints= ["URDFs_set/L_joint_continuous.urdf", "URDFs_set/L_joint_fixed.urdf", "URDFs_set/L_joint_revolute.urdf"]

    output_file = f"corrected_robot{i}.urdf"  # Modified URDF for each iteration
    modify_robot(input_file_body, input_file_limbs, input_file_limbs_joints, output_file)
    return output_file
