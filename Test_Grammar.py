import random

random.seed(90)

# Define the grammar rules as a dictionary.
# The keys are nonterminals (strings enclosed in "<" and ">") and the values
# are lists of possible productions (each production is a string of tokens).
grammar = {
    "<start>": ["<BodyStructure>"],
    "<BodyStructure>": ["body_Link_CUBE.urdf <FaceSet> <FaceSet> <FaceSet> <FaceSet> <FaceSet> <FaceSet>"],
    # Each FaceSet corresponds to one face of the cube.
    # It can be empty (no attachment), or attach a limb or a new body.
    "<FaceSet>": [
        "",
        "<L_Joint> <Limb> <FaceSet>",
        "<B_Joint> <BodyStructure>"
    ],
    # Body joints: choose one for attaching a new body.
    "<B_Joint>": [
        "B_joint_revolute.urdf",
        "B_joint_continuous.urdf",
        "B_joint_fixed.urdf"
    ],
    # Limb joints: choose one for attaching a limb.
    "<L_Joint>": [
        "L_joint_revolute.urdf",
        "L_joint_continuous.urdf",
        "L_joint_fixed.urdf",
        "L_joint_revolute_horizontal.urdf"
    ],
    # Limbs: choose one of the available limb types.
    "<Limb>": [
        "limb_Link.urdf",
        "limb_Link_Small.urdf",
        "wheel_link.urdf"
    ]
}


MAX_DEPTH = 5

def expand(symbol, depth):
    """
    Recursively expand a grammar symbol.
    :param symbol: The symbol to expand (a string).
    :param depth: Current recursion depth.
    :param used_spheres: A set of sphere filenames already used for the current body.
    :return: The expanded string.
    """
    indent = "  " * depth # For printing indentation based on recursion depth

    # If symbol is terminal (does not start with "<"), return it.
    if not symbol.startswith("<") or symbol not in grammar:
        print(f"{indent}Terminal: {symbol}")
        return symbol

    # If we have reached max depth and the symbol is any of the non-terminal, force terminal production.
    if depth >= MAX_DEPTH and (symbol.startswith("<")):
        production = symbol
        print(f"{indent}Depth {depth} reached for {symbol}, forcing production: {production}")
        return production
    else:
        options = grammar[symbol]
        production = random.choice(options)
        print(f"{indent}Expanding {symbol} at depth {depth} -> Chosen production: {production}")

    # Split the production into tokens.
    tokens = production.split()

    # This list will hold the expansion results for each token.
    result_tokens = []

    for token in tokens:
        # When starting a new body, create a fresh used_spheres set.
        print(f"{indent}Expanding new body!")
        result_tokens.append(expand(token, depth + 1))

    return " ".join(result_tokens)

def generate_robot():
    """
    Generate a complete URDF fragment from the grammar and print the expansion trace.
    """

    print("=== Starting Expansion from <start> ===")
    final_output = expand("<start>", 0)
    print("=== Expansion Complete ===")
    return final_output

if __name__ == "__main__":
    robot_urdf = generate_robot()
    print("\nGenerated URDF Fragment:")
    print(robot_urdf)


