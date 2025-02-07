import random

random.seed(101)

# Define the grammar rules as a dictionary.
# The keys are nonterminals (strings enclosed in "<" and ">") and the values
# are lists of possible productions (each production is a string of tokens).
grammar = {
    "<start>": ["<expr>"],
    "<expr>": [
        "<body>",
        "<body> <sphere_AUX_Body> <Add_B>",
        "<body> <sphere_AUX_Body> <Add_L>"
    ],
    "<body>": ["body_Link_CUBE.urdf"],
    "<sphere_AUX_Body>": [
        "sphere_auxiliar_Link_BACK.urdf",
        "sphere_auxiliar_Link_BOTTOM.urdf",
        "sphere_auxiliar_Link_FRONT.urdf",
        "sphere_auxiliar_Link_LEFT.urdf",
        "sphere_auxiliar_Link_RIGHT.urdf",
        "sphere_auxiliar_Link_TOP.urdf"
    ],
    # For limbs, the empty option is represented by an empty string.
    "<sphere_AUX_Links>": ["sphere_auxiliar_LIMBS.urdf"],
    "<Add_B>": ["<JointBody> <sphere_AUX_Body> <expr>"],
    "<Add_L>": ["<JointLimb> <sphere_AUX_Links> <Limbs>"],
    "<JointBody>": [
        "B_joint_revolute.urdf",
        "B_joint_continuous.urdf",
        "B_joint_fixed.urdf"
    ],
    "<JointLimb>": [
        "L_joint_revolute.urdf",
        "L_joint_continuous.urdf",
        "L_joint_fixed.urdf",
        "L_joint_revolute_horizontal.urdf"
    ],
    "<Limbs>": [
        "<Big_Link>",
        "<Small_Link>",
        "<Wheel_Link>",
        "<Big_Link> <sphere_AUX_Links> <Add_L>",
        "<Small_Link> <sphere_AUX_Links> <Add_L>",
        "<Wheel_Link> <sphere_AUX_Links> <Add_L>"
    ],
    "<Big_Link>": ["limb_Link.urdf"],
    "<Small_Link>": ["limb_Link_Small.urdf"],
    "<Wheel_Link>": ["wheel_link.urdf"]
}

MAX_DEPTH = 5

def expand(symbol, depth, used_spheres):
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

    # If we have reached max depth and the symbol is <expr>, force terminal production.
    if depth >= MAX_DEPTH and symbol == "<expr>":
        production = "<body>"
        print(f"{indent}Depth {depth} reached for {symbol}, forcing production: {production}")
    else:
        options = grammar[symbol]
        production = random.choice(options)
        print(f"{indent}Expanding {symbol} at depth {depth} -> Chosen production: {production}")

    # Split the production into tokens.
    tokens = production.split()

    # This list will hold the expansion results for each token.
    result_tokens = []

    for token in tokens:
        # Special handling for <sphere_AUX_Body>: we want to choose one that hasn't been used.
        if token == "<sphere_AUX_Body>":
            # Get all sphere options from grammar.
            sphere_options = grammar["<sphere_AUX_Body>"]
            # Filter out those already used.
            available = [opt for opt in sphere_options if opt not in used_spheres]
            if not available:
                # If all have been used, reset available options (or choose randomly among all).
                available = sphere_options
            chosen = random.choice(available)
            # Add the chosen sphere to the set so that it is not reused for the same body.
            used_spheres.add(chosen)
            print(f"{indent}  Chose sphere: {chosen}")
            result_tokens.append(chosen)
        else:
            # For other tokens, simply expand them recursively.
            # For nonterminals that represent a new body (<body>), reset the used_spheres set.
            if token == "<body>":
                # When starting a new body, create a fresh used_spheres set.
                print(f"{indent}  Expanding new body, resetting used spheres")
                result_tokens.append(expand(token, depth, set()))
            else:
                result_tokens.append(expand(token, depth + 1, used_spheres))
    return " ".join(result_tokens)

def generate_robot():
    """
    Generate a complete URDF fragment from the grammar and print the expansion trace.
    """
    used_spheres = set()  # Initial empty set for tracking sphere usage per body.
    print("=== Starting Expansion from <start> ===")
    final_output = expand("<start>", 0, used_spheres)
    print("=== Expansion Complete ===")
    return final_output

if __name__ == "__main__":
    robot_urdf = generate_robot()
    print("\nGenerated URDF Fragment:")
    print(robot_urdf)


