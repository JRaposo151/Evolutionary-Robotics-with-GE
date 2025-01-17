def generate_custom_urdf():
    urdf_template = """<?xml version="1.0" encoding="utf-8"?>
<robot name="random_robot">
{links_and_joints}
</robot>
"""

    # Link template with fixed names and parameters
    link_template = """
  <link name="{link_name}">
    <visual>
      <geometry>
        <cylinder length="{length}" radius="{radius}" />
      </geometry>
      <material name="{material_name}">
        <color rgba="{color}" />
      </material>
    </visual>
    <collision>
      <geometry>
        <cylinder length="{length}" radius="{radius}" />
      </geometry>
    </collision>
    <inertial>
      <mass value="{mass}" />
      <inertia ixx="{ixx}" ixy="0.0" ixz="0.0" iyy="{iyy}" iyz="0.0" izz="{izz}" />
    </inertial>
  </link>
"""

    # Joint template with fixed names and parameters
    joint_template = """
  <joint name="{joint_name}" type="{joint_type}">
    <parent link="{parent_link}" />
    <child link="{child_link}" />
    <origin xyz="0 0 0" rpy="0 0 0" />
    <axis xyz="0 0 1" />
    <limit lower="{lower_limit}" upper="{upper_limit}" effort="1.0" velocity="{velocity}" />
  </joint>
"""

    # Link and joint definitions based on earlier values
    links = [
        {"link_name": "base_link", "length": 0.0375, "radius": 0.01125, "mass": 1.0, "color": "1.0 0.0 0.0 1.0"},
        {"link_name": "link_1", "length": 0.0375, "radius": 0.00625, "mass": 0.5, "color": "0.0 0.0 1.0 1.0"},
        {"link_name": "link_2", "length": 0.0375, "radius": 0.00625, "mass": 0.5, "color": "0.0 0.0 1.0 1.0"},
        {"link_name": "link_3", "length": 0.0375, "radius": 0.00625, "mass": 0.5, "color": "0.0 0.0 1.0 1.0"},
        {"link_name": "link_4", "length": 0.0375, "radius": 0.00625, "mass": 0.5, "color": "0.0 0.0 1.0 1.0"},  # Added missing link_4
    ]

    joints = [
        {"joint_name": "joint_1", "joint_type": "fixed", "parent_link": "base_link", "child_link": "link_1", "lower_limit": 0.0, "upper_limit": 0.0, "velocity": 0.0},  # Base joint
        {"joint_name": "joint_2", "joint_type": "revolute", "parent_link": "link_1", "child_link": "link_2", "lower_limit": -3.14, "upper_limit": 3.14, "velocity": 1.0},
        {"joint_name": "joint_3", "joint_type": "prismatic", "parent_link": "link_2", "child_link": "link_3", "lower_limit": 0.0, "upper_limit": 0.05, "velocity": 0.5},
        {"joint_name": "joint_4", "joint_type": "revolute", "parent_link": "link_3", "child_link": "link_4", "lower_limit": -3.14, "upper_limit": 3.14, "velocity": 1.0},  # Fixed broken joint hierarchy
    ]

    # Generate links and joints
    link_definitions = []
    joint_definitions = []

    for link in links:
        inertia_value = link["mass"] / 12  # Simplified inertia calculation
        link_definitions.append(link_template.format(
            link_name=link["link_name"],
            length=link["length"],
            radius=link["radius"],
            material_name=link["link_name"] + "_material",
            color=link["color"],
            mass=link["mass"],
            ixx=inertia_value,
            iyy=inertia_value,
            izz=inertia_value,
        ))

    for joint in joints:
        joint_definitions.append(joint_template.format(
            joint_name=joint["joint_name"],
            joint_type=joint["joint_type"],
            parent_link=joint["parent_link"],
            child_link=joint["child_link"],
            lower_limit=joint["lower_limit"],
            upper_limit=joint["upper_limit"],
            velocity=joint["velocity"],
        ))

    # Combine links and joints into the URDF template
    full_urdf = urdf_template.format(links_and_joints="\n".join(link_definitions + joint_definitions))

    return full_urdf


# Generate and save the custom URDF
custom_urdf = generate_custom_urdf()
with open("custom_robot.urdf", "w") as f:
    f.write(custom_urdf)

print("Custom URDF generated and saved as 'custom_robot.urdf'")
