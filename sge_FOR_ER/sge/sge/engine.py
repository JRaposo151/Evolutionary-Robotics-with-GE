import os
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
from URDFs_set import Autonomous_Assembly_working


def generate_random_individual():
    genotype = [[] for key in grammar.get_non_terminals()]
    tree_depth = grammar.recursive_individual_creation(genotype, grammar.start_rule()[0], 0)

    return {'genotype': genotype, 'fitness': None, 'tree_depth' : tree_depth}


def make_initial_population():
    for i in range(params['POPSIZE']):
        yield generate_random_individual()


def evaluate(ind, eval_func, name):
    mapping_values = [0 for i in ind['genotype']]
    phen, tree_depth, tree = grammar.mapping(ind['genotype'], mapping_values)
    tree.hshow()
    """AQUI CONSTRUIR O ROBO COM AS TREES"""
    Autonomous_Assembly_working.assemblement(tree, name)
    ROBOT_PATH = f"../../sge/examples/robots/{name}.urdf"
    # TODO AQUI REVER E FAZER TREINO DE PPO E AVALIAÇÂO
    quality, other_info = eval_func.evaluate_robot(ROBOT_PATH, name)
    ind['phenotype'] = phen
    ind['fitness'] = quality
    ind['other_info'] = other_info
    ind['mapping_values']= mapping_values
    ind['tree_depth'] = tree_depth
    ind['name'] = f"robot_{name}.urdf"


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
    robot_DIR = "../examples/robots"
    setup(parameters_file_path=parameters_file)
    population = list(make_initial_population())
    it = 0
    robot_number = 0
    while it <= params['GENERATIONS']:
        mutation_rate = it / params['GENERATIONS']
        crossover_rate = 1 - mutation_rate
        for i in tqdm(population):
            name = f"GEN_{it}_number_{robot_number}"
            if i['fitness'] is None:

                # TODO AQUI É A FASE DE ENTAO TREINAR E AVALIAR OS ROBOTS PARA SE TER A FITNESS
                # TODO AQUI INICIALMENTE PSSO STRIBUIR A LA PATA
                """
                CONSTRUCTION OF THE POPULATION AND EVALUATION ---> FALTA A AVALIAÇÃO
                """
                evaluate(i, evaluation_function, name)
                robot_number += 1
        population.sort(key=lambda x: x['fitness'])
        logger.evolution_progress(it, population)

        # TODO AQUI TER ALGO QUE GUARDE O MELHOR INDIVIDUO / fenotipo ou arvore DE CADA GERAÇÃO, GUARDE O FITNESS

        # TODO PROCESOS DE SELEÇÂO -> DUVIDA AQUI NESTA SELECAO ????????????????????????????????????????????????????????????????????
        new_population = population[:params['ELITISM']]
        print(len(new_population))
        print(params['POPSIZE'])


        while len(new_population) < params['POPSIZE']:
            name = f"GEN_{it}_number_{robot_number}"
            print(len(new_population))

            #TODO VER SE ALGUMA COISA É CONSTRUIDA --> SIM É CONSTRUIDO
            if random.random() < crossover_rate:
                p1 = tournament(population, params['TSIZE'])
                p2 = tournament(population, params['TSIZE'])
                ni = crossover(p1, p2, name)
                robot_number += 1
            else:
                ni = tournament(population, params['TSIZE'])
            ni = mutate(ni, mutation_rate)

            # TODO FAZER AVALICAO PARA ENTAO ESTA NOVA POPULACAO TER FITNESS  AQUI ANTES DO APPEND
            new_population.append(ni)
        #TODO HA UM ERRO QUANDO O POPSIZE E MAIOR QUE 120 -> Erro com o valor de depth da arvore, ha um robo que esta a ficar muito grande
        new_population.sort(key=lambda x: x['fitness'])

        #TODO VER SE REALMENTE É NECESSARIO
        logger.evolution_progress(it, new_population)

        #TODO VER QUANTOS PASSAM REALMENTE
        population = new_population


        # TODO APOS TODOS PASSAREM PARA A PROXIMA GERAÇÃO, aqueles que nao passaram é pra apagar--->   DONE
        survivors = [ind["name"] for ind in population]
        for file in sorted(os.listdir(robot_DIR)):
            print(file)
            file_path = os.path.join(robot_DIR, file)
            # Check if the file is NOT in the list
            if file not in survivors:
                print(f"Deleting: {file}")
                os.remove(file_path)  # delete the file
            else:
                print(f"Keeping: {file}")

        it += 1