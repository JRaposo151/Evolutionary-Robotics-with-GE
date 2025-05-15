import random
from bigtree import Node

random.seed(82)


# Define the grammar rules as a dictionary.
# The keys are non-terminals (strings enclosed in "<" and ">") and the values
# are lists of possible productions (each production is a string of tokens).
grammar = {
    "<start>": ["<BodyStructure>"],
    # Each face represents one side of the cube. Only 5 here because one can be seen as the face/head of the robot
    "<BodyStructure>": ["body_Link_CUBE <FaceSet> <FaceSet> <FaceSet> <FaceSet> <FaceSet> <FaceSet>"],
    "<NewBodyStructure>": ["body_Link_CUBE <FaceSet> <FaceSet> <FaceSet> <FaceSet> <FaceSet>"],

    # Each face set can be empty or be directed for a new extension: a new body link or new limbs
    "<FaceSet>": [
        "ε",
        "<Extension>"
    ],

    "<Extension>": [
        "<BodyExtension>",
        "<LimbChain>"
    ],

    # This rules will have the objective to increase the body structure
    "<BodyExtension>": ["<B_Joint> <NewBodyStructure>"],

    # This rules and the next two will have the objective to add limbs and increase the total size of each one
    "<LimbChain>": ["<LimbAttachment> <LimbExtension>"],

    # A limb attachment is a limb joint followed by a limb component.
    "<LimbAttachment>": ["<L_Joint> <Limb>"],

    "<LimbExtension>": [
        "ε",
        "<L_Joint> <Limb> <LimbExtension>"
    ],

    "<B_Joint>": [
        "B_joint_revolute",
        "B_joint_continuous",
        "B_joint_fixed"
    ],

    "<L_Joint>": [
        "L_joint_revolute",
        "L_joint_continuous",
        "L_joint_fixed",
        "L_joint_continuous_horizontal"
    ],

    "<Limb>": [
        "limb_Link",
        "limb_Link_Small",
        "wheel_link"
    ]
}

MAX_DEPTH = 8
node_counter = 0  # Global counter to give unique IDs to nodes
tree = Node(f"{node_counter} ROOT")  # Global tree structure
parent = tree


def expand(symbol, depth, bodyN, new_bodies):
    """
    Recursively expand a grammar symbol.
    :param bodyN: The number of the new body which will be expanded.
    :param new_bodies: A list where new bodies are to be expanded.
    :param symbol: The symbol to expand (a string).
    :param depth: Current recursion depth.
    :return: The expanded string and the tree of the construction.
    """
    global node_counter, tree, parent
    face_counter = 0

    # If symbol is terminal (does not start with "<"), return it.
    if not symbol.startswith("<") or symbol not in grammar:
        if symbol != "body_Link_CUBE":
            node_name = f"{node_counter} {symbol}"
            node_counter += 1
            new_parent = Node(node_name, parent=parent)
            parent = new_parent
        else:
            node_name = f"{node_counter} {symbol}"
            node_counter += 1
            new_parent = Node(node_name, parent=parent)
            parent = new_parent
            new_bodies.append(new_parent)
        return symbol

    # If we have reached max depth and the symbol is any of the non-terminal, force terminal production.
    if depth >= MAX_DEPTH and symbol.startswith("<"):
        node_name = f"{node_counter}ε"
        node_counter += 1
        Node(node_name, parent=parent)
        return ""

    options = grammar[symbol]
    production = random.choice(options)

    # If the production is "ε", return an empty string immediately.
    if production.startswith("ε"):
        node_name = f"{node_counter} {production}"
        node_counter += 1
        Node(node_name, parent=parent)
        return ""

    # Split the production into tokens.
    tokens = production.split()

    # This list will hold the expansion results for each token.
    result_tokens = []

    for token in tokens:
        # Starting a new non-terminal symbol.
        if token == "<FaceSet>":
            face_counter += 1  # it helps debugging
            result_tokens.append("FaceSet:")
            parent = new_bodies[bodyN]
            if face_counter == 5 and not (parent.node_name.__contains__("1 body_Link_CUBE")):
                new_bodies.pop()
                bodyN -= 1
                print(parent.node_name)
        # Starting a new non-terminal symbol.
        if token == "body_Link_CUBE":
            bodyN += 1
        result_tokens.append(expand(token, depth + 1, bodyN, new_bodies))

    # This creates a new list filtered by spaces; each token different from "" will be included.
    results_tokens_filtered = [token for token in result_tokens if token.strip() != ""]
    return " ".join(results_tokens_filtered)


def generate_robot():
    """
    Generate a complete URDF fragment from the grammar.
    """
    global node_counter, tree, parent
    # Reset globals for each run:
    node_counter = 0
    tree = Node("0 ROOT")  # fresh tree with new root
    parent = tree


    node_counter += 1
    new_bodies = []
    final_output = expand("<start>", 0, -1, new_bodies)
    return final_output, tree


if __name__ == '__main__':
    final_str, tree_root = generate_robot()
    print("Final generated string:")
    print(final_str)
    print("\nFull tree structure:")
    tree_root.hshow()
