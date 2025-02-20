from robotExpansion_DSGE import robot_grammar_expansion
from URDFs_set import Autonomous_Assembly

robot_prototype = robot_grammar_expansion.generate_robot()

print("BEGINNING:::> " + robot_prototype + " <:::END")

#robot_product = Autonomous_Assembly.main(1)