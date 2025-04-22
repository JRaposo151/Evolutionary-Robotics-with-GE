import numpy as np
from sge_FOR_ER.sge.sge.parameters import params
import json
import os



def evolution_progress(generation, pop):
    fitness_samples = [i['fitness'] for i in pop]
    data = f'Generation:{generation:4d}, Min_Fitness_Samples:{np.min(fitness_samples):6e}, Mean_fitness:{np.mean(fitness_samples):6e}, STD_Fitness:{np.std(fitness_samples):6e}'
    if params['VERBOSE']:
        print(data)
    save_progress_to_file(data)
    if generation % params['SAVE_STEP'] == 0:
        save_step(generation, pop)


def save_progress_to_file(data):
    with open('%s/run_%d/progress_report.csv' % (params['EXPERIMENT_NAME'], params['RUN']), 'a') as f:
        f.write(data + '\n')


def save_step(generation, population):
    c = json.dumps(population)
    open('%s/run_%d/iteration_%d.json' % (params['EXPERIMENT_NAME'], params['RUN'], generation), 'a').write(c)


def save_parameters():
    params_lower = dict((k.lower(), v) for k, v in params.items())
    c = json.dumps(params_lower)
    open('%s/run_%d/parameters.json' % (params['EXPERIMENT_NAME'], params['RUN']), 'a').write(c)


def prepare_dumps():
    try:
        os.makedirs('%s/run_%d' % (params['EXPERIMENT_NAME'], params['RUN']))
    except FileExistsError as e:
        pass
    save_parameters()