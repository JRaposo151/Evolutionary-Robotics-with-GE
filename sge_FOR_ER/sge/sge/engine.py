import random
import sys
from sge_FOR_ER.sge.sge import grammar as grammar
from sge_FOR_ER.sge.sge import logger as logger
from datetime import datetime
from tqdm import tqdm
from sge_FOR_ER.sge.sge.operators.recombination import crossover
from sge_FOR_ER.sge.sge.operators.mutation import mutate
from sge_FOR_ER.sge.sge.operators.selection import tournament
from sge_FOR_ER.sge.sge.parameters import (
    params,
    set_parameters,
    load_parameters
)
from bigtree import Node



def generate_random_individual():
    genotype = [[] for key in grammar.get_non_terminals()]
    tree = Node("0 ROOT")
    tree_depth = grammar.recursive_individual_creation(genotype, grammar.start_rule()[0], 0)

    return {'genotype': genotype, 'fitness': None, 'tree_depth' : tree_depth, 'tree' : tree}


def make_initial_population():
    for i in range(params['POPSIZE']):
        yield generate_random_individual()


def evaluate(ind, eval_func):
    mapping_values = [0 for i in ind['genotype']]
    phen, tree_depth, tree = grammar.mapping(ind['genotype'], mapping_values)
    tree.hshow()
    """AQUI CONSTRUIR O ROBO COM AS TREES"""
    from URDFs_set import Autonomous_Assembly_working
    Autonomous_Assembly_working.assemblement(tree,20)

    quality, other_info = eval_func.evaluate(phen)
    ind['phenotype'] = phen
    ind['tree'] = tree
    ind['fitness'] = quality
    ind['other_info'] = other_info
    ind['mapping_values']= mapping_values
    ind['tree_depth'] = tree_depth


def setup(parameters_file_path = None):
    if parameters_file_path is not None:
        load_parameters(file_name=parameters_file_path)
    set_parameters(sys.argv[1:])
    if params['SEED'] is None:
        params['SEED'] = int(datetime.now().microsecond)
    logger.prepare_dumps()
    random.seed(params['SEED'])
    grammar.set_path(params['GRAMMAR'])
    grammar.read_grammar()
    grammar.set_max_tree_depth(params['MAX_TREE_DEPTH'])
    grammar.set_min_init_tree_depth(params['MIN_TREE_DEPTH'])


def evolutionary_algorithm(evaluation_function=None, parameters_file=None):
    setup(parameters_file_path=parameters_file)
    population = list(make_initial_population())
    it = 0
    while it <= params['GENERATIONS']:
        for i in tqdm(population):
            if i['fitness'] is None:

                # TODO AQUI É A FASE DE ENTAO TREINAR E AVALIAR OS ROBOTS PARA SE TER A FITNESS
                # TODO AQUI INICIALMENTE PSSO STRIBUIR A LA PATA
                evaluate(i, evaluation_function)
        population.sort(key=lambda x: x['fitness'])

        logger.evolution_progress(it, population)

        #TODO PROCESOS DE SELEÇÂO
        new_population = population[:params['ELITISM']]
        while len(new_population) < params['POPSIZE']:


            #TODO AQUI ENTAO CRIAR PROCESSO AUTOMATICO DE CROSSOVER / NOVA CONSTRUÇAO E AINDA VER A MUTÇÂO
            if random.random() < params['PROB_CROSSOVER']:
                p1 = tournament(population, params['TSIZE'])
                p2 = tournament(population, params['TSIZE'])
                ni = crossover(p1, p2)
            else:
                ni = tournament(population, params['TSIZE'])
            ni = mutate(ni, params['PROB_MUTATION'])
            new_population.append(ni)
        population = new_population
        it += 1

