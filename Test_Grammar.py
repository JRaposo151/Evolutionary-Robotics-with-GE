import random

random.seed(90)

# Define the grammar rules as a dictionary.
# The keys are nonterminals (strings enclosed in "<" and ">") and the values
# are lists of possible productions (each production is a string of tokens).
grammar = {
    "<start>": ["<BodyStructure>"],
    # A body is a cube with five face attachment slots.
    "<BodyStructure>": ["body_Link_CUBE.urdf <FaceSet> <FaceSet> <FaceSet> <FaceSet> <FaceSet>"],

    # Each FaceSet corresponds to one face of the cube. It may be empty or contain an extension.
    "<FaceSet>": [
        " ",
        "<Extension>"
    ],

    # An extension can either attach a new body or add a limb chain.
    "<Extension>": [
        "<BodyExtension>",
        "<LimbChain>"
    ],

    # A body attachment uses a body joint and then adds a new body.
    "<BodyExtension>": ["<B_Joint> <BodyStructure>"],

    # A limb chain consists of an initial limb attachment followed by an optional extension.
    "<LimbChain>": ["<LimbAttachment> <LimbExtension>"],

    # A limb attachment is a limb joint followed by a limb component.
    "<LimbAttachment>": ["<L_Joint> <Limb>"],

    # A limb extension may be empty or recursively add another limb joint and limb.
    "<LimbExtension>": [
        " ",
        "<L_Joint> <Limb> <LimbExtension>"
    ],

    # Body joints for attaching a new body.
    "<B_Joint>": [
        "B_joint_revolute.urdf",
        "B_joint_continuous.urdf",
        "B_joint_fixed.urdf"
    ],

    # Limb joints for attaching limbs or extending a limb chain.
    "<L_Joint>": [
        "L_joint_revolute.urdf",
        "L_joint_continuous.urdf",
        "L_joint_fixed.urdf",
        "L_joint_revolute_horizontal.urdf"
    ],

    # Limb elements: choose one of the available limb types.
    "<Limb>": [
        "limb_Link.urdf",
        "limb_Link_Small.urdf",
        "wheel_link.urdf"
    ]
}


MAX_DEPTH = 8

def expand(symbol, depth):
    """
    Recursively expand a grammar symbol.
    :param symbol: The symbol to expand (a string).
    :param depth: Current recursion depth.
    :param used_spheres: A set of sphere filenames already used for the current body.
    :return: The expanded string.
    """
    indent = "  " * depth # For printing indentation based on recursion depth
    facesetCounter = 0

    # If symbol is terminal (does not start with "<"), return it.
    if not symbol.startswith("<") or symbol not in grammar:
        print(f"{indent}Terminal: {symbol}")
        return symbol

    # If we have reached max depth and the symbol is any of the non-terminal, force terminal production.
    if depth >= MAX_DEPTH and (symbol.startswith("<")):
        production = symbol
        if symbol.startswith("<FaceSet>"):
            facesetCounter +=1
            print(f"{indent}Depth {depth} reached for {symbol}_{facesetCounter}, forcing production: {production}")
        else:
            print(f"{indent}Depth {depth} reached for {symbol}, forcing production: {production}")
        return production
    else:
        options = grammar[symbol]
        production = random.choice(options)
        if production.startswith(" ") and symbol.startswith("<FaceSet>"):
            print(f"{indent}Expanding {symbol}_{facesetCounter} at depth {depth} -> Chosen production: NONE")
        elif symbol.startswith("<FaceSet>"):
            print(f"{indent}Expanding {symbol}_{facesetCounter} at depth {depth} -> Chosen production:  {production}")
        else:
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


