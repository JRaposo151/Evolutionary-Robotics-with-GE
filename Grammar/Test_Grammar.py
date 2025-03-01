import random

random.seed(90)

# Define the grammar rules as a dictionary.
# The keys are nonterminals (strings enclosed in "<" and ">") and the values
# are lists of possible productions (each production is a string of tokens).
grammar = {
    "<start>": ["<BodyStructure>"],
    # Each face represents one side of the cube. Only 5 here because one can be seen as the face/head of the robot
    "<BodyStructure>": ["body_Link_CUBE <FaceSet> <FaceSet> <FaceSet> <FaceSet> <FaceSet> <FaceSet>"],

    # Each face set can be empty or be directed for a new extension: a new body link or new limbs
    "<FaceSet>": [
        "ε",
        "<Extension>"
    ],


    "<Extension>": [
        "<BodyExtension>",
        "<LimbChain>"
    ],

    # This rules will have the objective to increase the body strucutre
    "<BodyExtension>": ["<B_Joint> <BodyStructure>"],

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

def expand(symbol, depth, facesetCounter):
    """
    Recursively expand a grammar symbol.
    :param symbol: The symbol to expand (a string).
    :param depth: Current recursion depth.
    :param facesetCounter: The faceset counter of the cube.
    :return: The expanded string.
    """
    indent = "  " * depth # For printing indentation based on recursion depth

    # If symbol is terminal (does not start with "<"), return it.
    if not symbol.startswith("<") or symbol not in grammar:
        print(f"{indent}Terminal: {symbol}")
        return symbol

    # If we have reached max depth and the symbol is any of the non-terminal, force terminal production.
    if depth >= MAX_DEPTH and (symbol.startswith("<")):
        if symbol.startswith("<FaceSet>"):
            print(f"{indent}Depth {depth} reached for {symbol}_{facesetCounter}, forcing production: {symbol}")
        else:
            print(f"{indent}Depth {depth} reached for {symbol}, forcing production: {symbol}")
        return symbol
    else:
        options = grammar[symbol]
        production = random.choice(options)
        if production.startswith("ε"):
            if symbol.startswith("<FaceSet>"):
                print(f"{indent}Expanding {symbol}_{facesetCounter} at depth {depth} -> Chosen production: NONE")
            elif symbol.startswith("<LimbExtension>"):
                print(f"{indent}Expanding {symbol} at depth {depth} -> Chosen production: NONE")
            return ""
        elif symbol.startswith("<FaceSet>"):
            print(f"{indent}Expanding {symbol}_{facesetCounter} at depth {depth} -> Chosen production:  {production}")
        else:
            print(f"{indent}Expanding {symbol} at depth {depth} -> Chosen production: {production}")

    # Split the production into tokens.
    tokens = production.split()


    # This list will hold the expansion results for each token.
    result_tokens = []

    for token in tokens:
        # Starting a new non-terminal symbol.
        if token == "<FaceSet>":
            facesetCounter += 1
            result_tokens.append("FaceSet:")
        print(f"{indent}Expanding new non-terminal: {token}!")
        result_tokens.append(expand(token, depth + 1, facesetCounter))

    results_tokens_filtered = [token for token in result_tokens if token.strip() != ""] # this create a new list filtered by spaces, each token different then "" will be included on it
    return " ".join(results_tokens_filtered)

def generate_robot():
    """
    Generate a complete URDF fragment from the grammar and print the expansion trace.
    """
    print("=== Starting Expansion from <start> ===")
    final_output = expand("<start>", 0, 0)
    print("=== Expansion Complete ===")
    return final_output

if __name__ == "__main__":
    robot_urdf = generate_robot()
    print("\nGenerated URDF Fragment:")
    print("BEGINNING:::> " + robot_urdf + " <:::END")


