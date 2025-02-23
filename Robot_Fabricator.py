from robotExpansion_DSGE import robot_grammar_expansion_2
from URDFs_set import Autonomous_Assembly_working

robot_prototype, robot_tree = robot_grammar_expansion_2.generate_robot()
print("Final generated string:")
print("BEGINNING:::> " + robot_prototype + " <:::END")

print("\nFull tree structure:")
robot_tree.hshow()

print(len(robot_prototype.split())) # TODO aqui este numero tem de ser o numero de conjuntos de regras e nao o numero de regras
robot_product = Autonomous_Assembly_working.main(robot_prototype)