import random
import sge_FOR_ER.sge.sge.grammar as grammar
from URDFs_set import Autonomous_Assembly_working
import copy

import math

def crossover(p1, p2, robot_number):
    xover_ratio = random.random()
    gen_size = len(p1['genotype'])

    child_genotype = []

    for gi in range(gen_size):
        g1 = p1['genotype'][gi]
        g2 = p2['genotype'][gi]

        # --- empty gene ---
        if not g1 and not g2:
            child_genotype.append([])
            continue

        # --- only one parent has gene ---
        if not g1:
            child_genotype.append(g2[:])
            continue
        if not g2:
            child_genotype.append(g1[:])
            continue


        # --- compute crossover point ---
        k1 = max(1, int(round(xover_ratio * len(g1))))
        k2 = max(1, int(round(xover_ratio * len(g2))))

        # --- one-point crossover (prefix) ---
        new_gene = g1[:k1] + g2[k2:]

        child_genotype.append(new_gene)

    mapping_values = [0] * gen_size


    # compute nem individual
    _, tree_depth, tree = grammar.mapping(child_genotype, mapping_values)
    Autonomous_Assembly_working.assemblement(tree, robot_number)
    return {'genotype': child_genotype, 'fitness': None, 'mapping_values': mapping_values,'name':"robot_"+robot_number, 'tree_depth': tree_depth}

