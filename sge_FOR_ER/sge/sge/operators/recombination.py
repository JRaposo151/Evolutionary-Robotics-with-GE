import random
import sge_FOR_ER.sge.sge.grammar as grammar
from URDFs_set import Autonomous_Assembly_working


def crossover(p1, p2, robot_number):
    xover_p_value = 0.5
    gen_size = len(p1['genotype'])
    mask = [random.random() for i in range(gen_size)]
    genotype = []
    for index, prob in enumerate(mask):
        if prob < xover_p_value:
            genotype.append(p1['genotype'][index][:])
        else:
            genotype.append(p2['genotype'][index][:])
    mapping_values = [0] * gen_size
    # compute nem individual
    _, tree_depth, tree = grammar.mapping(genotype, mapping_values)
    Autonomous_Assembly_working.assemblement(tree, robot_number)
    return {'genotype': genotype, 'fitness': None, 'mapping_values': mapping_values,'name':"robot_"+robot_number, 'tree_depth': tree_depth}