import random
from robotExpansion_DSGE import robot_grammar_expansion_2, robot_grammar_expansion_3
from URDFs_set import Autonomous_Assembly_working
from URDFs_set import Autonomous_Assembly

print("Robot Fabricator Started: ")
for i in range(11):
    random.seed(80 + i)
    print("Seed number: " + str(80 + i))
    robot_prototype, robot_tree = robot_grammar_expansion_3.generate_robot()
    print("Final generated string:")
    print("BEGINNING:::> " + robot_prototype + " <:::END")
    print("\nFull tree structure:")
    robot_tree.hshow()


    """
    É de notar que:
        -> o robot_grammar_expansion_2 esta com as regras gramaticais com as 6 faces e sempre a funcionar com as 6 faces;
        -> o robot_grammar_expansion_3 esta com as regras gramaticais novas com as 5 faces;
        -> o Autonomous_Assembly_working é o mais atual sendo que tem as regras para novo cubo quando adicionado, anotando qual o lado ocupado
    """
    #robot_product = Autonomous_Assembly.assemblement(robot_tree, i)
    robot_product = Autonomous_Assembly_working.assemblement(robot_tree, i)
