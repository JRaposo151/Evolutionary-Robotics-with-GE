import xml.etree.ElementTree as ET


def create_robot():
    robot = ET.Element("robot", name="BODY_LINK")

    # Base body link
    body_link = ET.SubElement(robot, "link", name="body_link")
    add_cylinder(body_link, length="0.1875", radius="0.05625", color="red", mass="5.0", inertia="0.025")

    # Top sphere joint
    top_joint = ET.SubElement(robot, "joint", name="top_sphere_joint_body", type="fixed")
    ET.SubElement(top_joint, "parent", link="body_link")
    ET.SubElement(top_joint, "child", link="body_joint_link")
    ET.SubElement(top_joint, "origin", xyz="0 0 0.0875", rpy="1.5 0 0")

    # Body joint link
    body_joint_link = ET.SubElement(robot, "link", name="body_joint_link")
    add_sphere(body_joint_link, radius="0.05", color="black", mass="0.5", inertia="0.0025")

    # Continuous joint
    continuous_joint = ET.SubElement(robot, "joint", name="continuous_joint", type="continuous")
    ET.SubElement(continuous_joint, "parent", link="body_joint_link")
    ET.SubElement(continuous_joint, "child", link="auxiliar")
    ET.SubElement(continuous_joint, "origin", xyz="0 0 0", rpy="1.6 0 0")
    ET.SubElement(continuous_joint, "axis", xyz="0 0 1")

    # Auxiliar link
    auxiliar_link = ET.SubElement(robot, "link", name="auxiliar")
    add_cylinder(auxiliar_link, length="0.07", radius="0.05", color="black", mass="0.5", inertia="0.0025")

    # Fixed joint
    fixed_joint = ET.SubElement(robot, "joint", name="fixed_joint", type="fixed")
    ET.SubElement(fixed_joint, "parent", link="auxiliar")
    ET.SubElement(fixed_joint, "child", link="limb_joint_bottom_blue_link")
    ET.SubElement(fixed_joint, "origin", xyz="0 0 -0.15", rpy="0 0 0")

    # Limb joint bottom blue link
    limb_joint_bottom_blue_link = ET.SubElement(robot, "link", name="limb_joint_bottom_blue_link")
    add_sphere(limb_joint_bottom_blue_link, radius="0.03125", color="blue", mass="2.5", inertia="0.0125")

    # Bottom sphere joint limb
    bot_sphere_joint_limb = ET.SubElement(robot, "joint", name="bot_sphere_joint_limb", type="fixed")
    ET.SubElement(bot_sphere_joint_limb, "parent", link="limb_joint_bottom_blue_link")
    ET.SubElement(bot_sphere_joint_limb, "child", link="limb_link")
    ET.SubElement(bot_sphere_joint_limb, "origin", xyz="0 0 0.09", rpy="0 0 0")

    # Limb link
    limb_link = ET.SubElement(robot, "link", name="limb_link")
    add_cylinder(limb_link, length="0.1875", radius="0.03125", color="blue", mass="2.5", inertia="0.0125")

    return robot


def add_cylinder(link, length, radius, color, mass, inertia):
    visual = ET.SubElement(link, "visual")
    geometry = ET.SubElement(visual, "geometry")
    ET.SubElement(geometry, "cylinder", length=length, radius=radius)
    material = ET.SubElement(visual, "material", name=color)
    ET.SubElement(material, "color", rgba=color_to_rgba(color))

    collision = ET.SubElement(link, "collision")
    geometry = ET.SubElement(collision, "geometry")
    ET.SubElement(geometry, "cylinder", length=length, radius=radius)

    inertial = ET.SubElement(link, "inertial")
    ET.SubElement(inertial, "mass", value=mass)
    ET.SubElement(inertial, "inertia", ixx=inertia, ixy="0.0", ixz="0.0", iyy=inertia, iyz="0.0", izz=inertia)


def add_sphere(link, radius, color, mass, inertia):
    visual = ET.SubElement(link, "visual")
    geometry = ET.SubElement(visual, "geometry")
    ET.SubElement(geometry, "sphere", radius=radius)
    material = ET.SubElement(visual, "material", name=color)
    ET.SubElement(material, "color", rgba=color_to_rgba(color))

    collision = ET.SubElement(link, "collision")
    geometry = ET.SubElement(collision, "geometry")
    ET.SubElement(geometry, "sphere", radius=radius)

    inertial = ET.SubElement(link, "inertial")
    ET.SubElement(inertial, "mass", value=mass)
    ET.SubElement(inertial, "inertia", ixx=inertia, ixy="0.0", ixz="0.0", iyy=inertia, iyz="0.0", izz=inertia)


def color_to_rgba(color):
    colors = {
        "red": "1.0 0.0 0.0 1.0",
        "black": "0.0 0.0 0.0 1.0",
        "blue": "0.0 0.0 1.0 1.0",
    }
    return colors.get(color, "1.0 1.0 1.0 1.0")


def save_robot_to_file(robot, filename):
    tree = ET.ElementTree(robot)
    ET.indent(tree, space="  ", level=0)
    tree.write(filename, encoding="utf-8", xml_declaration=True)


robot = create_robot()
save_robot_to_file(robot, "corrected_robot.urdf")



