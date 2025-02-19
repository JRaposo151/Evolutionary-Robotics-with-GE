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

    # This rules will have the objective to increase the body structure
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
        "L_joint_revolute_horizontal"
    ],

    "<Limb>": [
        "limb_Link",
        "limb_Link_Small",
        "wheel_link"
    ]
}

MAX_DEPTH = 8

def expand(symbol, depth):
    """
    Recursively expand a grammar symbol.
    :param symbol: The symbol to expand (a string).
    :param depth: Current recursion depth.
    :param facesetCounter: Counter for FaceSet occurrences.
    :return: The expanded string.
    """
    # If symbol is terminal (does not start with "<"), return it.
    if not symbol.startswith("<") or symbol not in grammar:
        return symbol

    # If we have reached max depth and the symbol is any of the non-terminal, force terminal production.
    if depth >= MAX_DEPTH and symbol.startswith("<"):
        return symbol

    options = grammar[symbol]
    production = random.choice(options)

    # If the production is "ε", return an empty string immediately.
    if production.startswith("ε"):
        return ""

    # Split the production into tokens.
    tokens = production.split()

    # This list will hold the expansion results for each token.
    result_tokens = []

    for token in tokens:
        # Starting a new non-terminal symbol.
        result_tokens.append(expand(token, depth + 1))

    # This creates a new list filtered by spaces; each token different from "" will be included.
    results_tokens_filtered = [token for token in result_tokens if token.strip() != ""]
    return " ".join(results_tokens_filtered)

def generate_robot():
    """
    Generate a complete URDF fragment from the grammar.
    """
    final_output = expand("<start>", 0)
    return final_output

if __name__ == "__main__":
    robot_urdf = generate_robot()
    print("BEGINNING:::> " + robot_urdf + " <:::END")
