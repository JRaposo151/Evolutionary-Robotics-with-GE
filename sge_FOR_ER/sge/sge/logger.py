import re

import numpy as np
from sge_FOR_ER.sge.sge.parameters import params
import json
import os

import matplotlib.pyplot as plt


def evolution_progress(generation, pop):
    fitness_samples = [i['fitness'] for i in pop]
    min_fitness = np.min(fitness_samples)
    mean_fitness = np.mean(fitness_samples)
    std_fitness = np.std(fitness_samples)
    best_fitness = np.max(fitness_samples)  # or min, depending on optimization goal
    data = (
        f'Generation:{generation:4d}, '
        f'Min_Fitness_Samples:{min_fitness:6e}, '
        f'Mean_fitness:{mean_fitness:6e}, '
        f'STD_Fitness:{std_fitness:6e}, '
        f'Best_Fitness:{best_fitness:6e}'
    )
    if params['VERBOSE']:
        print(data)
    save_progress_to_file(data)
    if generation % params['SAVE_STEP'] == 0:
        save_step(generation, pop)


def save_progress_to_file(data):
    with open('%s/run_%d/progress_report.csv' % (params['EXPERIMENT_NAME'], params['RUN']), 'a') as f:
        f.write(data + '\n')


def convert_numpy(obj):
    if isinstance(obj, np.generic):  # Handles np.float32, np.int64, etc.
        return obj.item()
    elif isinstance(obj, np.ndarray):  # Handles arrays (if any)
        return obj.tolist()
    raise TypeError(f"Object of type {type(obj)} is not JSON serializable")

def save_step(generation, population):
    c = json.dumps(population, default=convert_numpy)
    output_path = '%s/run_%d/iteration_%d.json' % (params['EXPERIMENT_NAME'], params['RUN'], generation)
    with open(output_path, 'a') as f:
        f.write(c)


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

def plot_progress_report():
    file_path = '%s/run_%d/progress_report.csv' % (params['EXPERIMENT_NAME'], params['RUN'])
    generations = []
    best_fitness = []
    avg_fitness = []
    std_fitness = []

    with open(file_path, 'r') as f:
        for line in f:
            # Extract values using regex
            match = re.search(
                r"Generation:\s*(\d+),\s*Min_Fitness_Samples:([-+eE0-9.]+),\s*Mean_fitness:([-+eE0-9.]+),\s*STD_Fitness:([-+eE0-9.]+),\s*Best_Fitness:([-+eE0-9.]+)",
                line
            )
            if match:
                gen = int(match.group(1))
                mean = float(match.group(3))
                std = float(match.group(4))
                best = float(match.group(5))

                generations.append(gen)
                avg_fitness.append(mean)
                std_fitness.append(std)
                best_fitness.append(best)

    generations = np.array(generations)
    best_fitness = np.array(best_fitness)
    avg_fitness = np.array(avg_fitness)
    std_fitness = np.array(std_fitness)

    # Plotting
    plt.figure(figsize=(10, 6))
    plt.plot(generations, best_fitness, label="Best Fitness", color='blue', marker='o')
    plt.plot(generations, avg_fitness, label="Average Fitness", color='orange', linestyle='--')
    plt.fill_between(generations,
                     avg_fitness - std_fitness,
                     avg_fitness + std_fitness,
                     color='orange', alpha=0.3, label="±1 Std Dev")

    plt.title("Best and Average Fitness Over Generations")
    plt.xlabel("Generation")
    plt.ylabel("Fitness (Distance)")
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    output_dir = "plots"
    os.makedirs(output_dir, exist_ok=True)
    plt.savefig(os.path.join(output_dir, f"fitness_plot_run_{params['RUN']}.png"), dpi=300)
    plt.show()
    plt.close()

