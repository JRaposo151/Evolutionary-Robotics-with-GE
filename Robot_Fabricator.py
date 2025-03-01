import random
from robotExpansion_DSGE import robot_grammar_expansion_2
from URDFs_set import Autonomous_Assembly_working
from URDFs_set import Autonomous_Assembly

print("Robot Fabricator Started: ")
for i in range(11):
    random.seed(80 + i)
    print("Seed number: " + str(80 + i))
    robot_prototype, robot_tree = robot_grammar_expansion_2.generate_robot()
    print("Final generated string:")
    print("BEGINNING:::> " + robot_prototype + " <:::END")
    print("\nFull tree structure:")
    robot_tree.hshow()
    """
    FALTA AQUI DEPOIS QUANTOS ROBOS DEVEM DE SER CONSTRUIDOS, NESTE CASO SE CALHAR UMA LISTA COM TODAS AS ARVORES PRODUZIDAS
    """
    #robot_product = Autonomous_Assembly.assemblement(robot_tree, 1)
    robot_product = Autonomous_Assembly_working.assemblement(robot_tree, i)
