import xml.etree.ElementTree as ET


def generate_urdf_files():
    # Define the three output file names
    urdf_filenames = ["file1.urdf", "file2.urdf", "file3.urdf"]

    # Define the list of information to add in separate loops
    info_list = ["XXX", "YYY", "WWW"]

    # Loop over each file name
    for i, filename in enumerate(urdf_filenames, start=1):
        # Create the root element, e.g., <robot name="robot_1">
        root = ET.Element("robot", name=f"robot_{i}")

        # Use a loop to append info in stages
        # 1st iteration: add "XXX"
        # 2nd iteration: add "YYY"
        # 3rd iteration: add "WWW"
        for info in info_list:
            info_element = ET.SubElement(root, "info")
            info_element.text = info

        # Build the tree and write to file
        tree = ET.ElementTree(root)
        tree.write(filename, encoding="utf-8", xml_declaration=True)
        print(f"Generated {filename}")


if __name__ == "__main__":
    generate_urdf_files()
