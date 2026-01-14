import os
import random
import shutil
import sys
from pathlib import Path

import numpy as np
import pybullet as p
import pybullet_data

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
from URDFs_set import Autonomous_Assembly_working_simmetry


def generate_random_individual():
    genotype = [[] for key in grammar.get_non_terminals()]
    tree_depth = grammar.recursive_individual_creation(genotype, grammar.start_rule()[0], 0)

    return {'genotype': genotype, 'fitness': None, 'tree_depth' : tree_depth}


def make_initial_population():
    for i in range(params['POPSIZE']):
        yield generate_random_individual()


def evaluate(ind, eval_func, name, n_generation):
    mapping_values = [0 for i in ind['genotype']]
    phen, tree_depth, tree = grammar.mapping(ind['genotype'], mapping_values)
    tree.hshow()
    failed_build = False
    """AQUI CONSTRUIR O ROBO COM AS TREES"""
    try:
        # Attempt to build the robot
        Autonomous_Assembly_working_simmetry.assemblement(tree, name)

    except Exception as e:
        print(f"[ASSEMBLY ERROR] Failed to assemble robot_{name}: {e}")
        failed_build = True
        # Save failed robot tree or partial URDF if available
        failed_dir = "failed_assemblies"
        os.makedirs(failed_dir, exist_ok=True)
        urdf_path = os.path.join("/workspace/URDFs_set", f"robot_{name}.urdf")
        if os.path.exists(urdf_path):
            shutil.copy(urdf_path, os.path.join(failed_dir, f"robot_{name}.urdf"))
            print(f"[SAVED] Partial or failed URDF saved: {urdf_path}")
        else:
            print(f"[WARN] No URDF found for robot_{name} — skipping save.")
            ind['fitness'] = 0
            ind['fitness'] = float(ind['fitness'])
            failed_build = False
            ind['phenotype'] = phen
            ind['mapping_values'] = mapping_values
            ind['tree_depth'] = tree_depth
            ind['name'] = f"robot_{name}.urdf"
            return


    # Absolute path to the URDF
    script_dir = Path(__file__).resolve().parent  # sge/
    ROBOT_PATH = script_dir.parent / "examples" / "robots" / f"robot_{name}.urdf"
    plane = 1                       # here is to switch between planes: horizontal or mountains
    if not ROBOT_PATH.is_file():
        raise FileNotFoundError(f"URDF not found: {ROBOT_PATH}")

    if not has_movable_joints(ROBOT_PATH):
        ind['fitness'] = 0
        ind['fitness'] = float(ind['fitness'])
    else:
        quality, other_info = eval_func.evaluate_robot(str(ROBOT_PATH), f"robot_{name}", n_generation, plane)
        ind['fitness'] = quality
        ind['fitness'] = float(ind['fitness'])
        ind['other_info'] = other_info
    ind['phenotype'] = phen
    ind['mapping_values'] = mapping_values
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

def has_movable_joints(robot_path):
    p.connect(p.DIRECT)
    p.setAdditionalSearchPath(pybullet_data.getDataPath())
    # Parse the URDF to check for movable joints
    robot = p.loadURDF(str(robot_path))
    joints = p.getNumJoints(robot)
    movable_joints = [
        j for j in range(joints)
        if p.getJointInfo(robot, j)[2] in [0]]
    p.disconnect()
    return len(movable_joints) > 0

def evolutionary_algorithm(evaluation_function=None, parameters_file=None):
    robot_DIR = "../examples/robots"
    setup(parameters_file_path=parameters_file)
    population = list(make_initial_population())
    it = 0
    robot_number = 0
    import json
    import os
    directory = '/home/joaoraposo/Documents/GitHub/Evolutionary-Robotics-with-GE/sge_FOR_ER/sge/examples/dumps/Test'
    if not os.listdir(directory):
        print("Directory is empty")
    else:
        print("Directory is not empty")
        # === 1. Load saved population from previous generation ===
        checkpoint_path = directory + "/run_1/iteration_22.json"
        with open(checkpoint_path, "r") as f:
            population = json.load(f)

        # === 2. Set the generation number (based on the file) ===
        # Extract generation number from filename (e.g., iteration_3.json → 4)
        it = int(os.path.splitext(os.path.basename(checkpoint_path))[0].split("_")[1])
        # === 3. Get the last robot number from the loaded population ===
        last_ind = population[-1]  # last individual in the list
        robot_name = last_ind['name']  # e.g., "robot_GEN_0_number_51.urdf"

        #Extract the number from the name string
        robot_numbers = [
            int(ind['name'].split("_")[-1].split(".")[0])
            for ind in population
        ]

        # Get the biggest robot number and increment
        robot_number = max(robot_numbers) + 1


    while it <= params['GENERATIONS']:
        mutation_rate = it / params['GENERATIONS']
        crossover_rate = params['PROB_CROSSOVER'] - mutation_rate
        for i in tqdm(population):
            name = f"GEN_{it}_number_{robot_number}"
            if i['fitness'] is None:
                """
                CONSTRUCTION OF THE POPULATION AND EVALUATION
                """
                evaluate(i, evaluation_function, name, it)
                robot_number += 1

        population.sort(key=lambda x: x['fitness'], reverse=True)
        logger.evolution_progress(it, population)

        new_population = population[:params['ELITISM']]
        #print(len(new_population))
        #print(params['POPSIZE'])
        while len(new_population) < params['POPSIZE']:
            name = f"GEN_{it}_number_{robot_number}"
            if random.random() < crossover_rate:
                p1 = tournament(population, params['TSIZE'])
                p2 = tournament(population, params['TSIZE'])
                ni = crossover(p1, p2, name)
                robot_number += 1
            else:
                ni = tournament(population, params['TSIZE'])
            ni = mutate(ni, mutation_rate)
            new_population.append(ni)

        population = new_population
        robots = "../examples/robots"
        brain_paths = "../examples/robots_brains"
        vec_paths = "../examples/robots_vec"
        ind_save_path = "../examples/robots_ind"
        paths = [robot_DIR,brain_paths, vec_paths]
        survivors = [os.path.splitext(ind['name'])[0] for ind in population]
        for path in paths:
            for file in sorted(os.listdir(path)):
                file_path = os.path.join(path, file)
                base_name = os.path.splitext(file)[0]
                # Check if the file is NOT in the list
                if base_name not in survivors:
                    print(f"Deleting: {file}")
                    os.remove(file_path)  # delete the file
                else:
                    print(f"Keeping: {file}")

        os.makedirs(ind_save_path, exist_ok=True)
        import shutil
        # Find best individual of current generation
        valid_inds = [ind for ind in population if ind['fitness'] is not None]
        if valid_inds:
            best_ind = max(valid_inds, key=lambda ind: ind['fitness'])
        else:
            print("No valid individuals with fitness found.")
            best_ind = None  # or handle this differently
        # Extract base name without extension (e.g., robot_GEN_000_number_0)
        base_name = os.path.splitext(best_ind['name'])[0]
        generation_number = it
        gen_str = f"{generation_number:03d}"
        save_prefix = f"best_gen_{gen_str}"
        save_path = os.path.join(ind_save_path, save_prefix)

        # Copy URDF from robots/
        urdf_source = os.path.join(robots, f"{base_name}.urdf")
        urdf_dest = f"{save_path}.urdf"
        if os.path.exists(urdf_source):
            shutil.copy2(urdf_source, urdf_dest)
        else:
            print(f"[WARNING] URDF not found: {urdf_source}")

        # Copy PKL from vec_paths
        pkl_source = os.path.join(vec_paths, f"{base_name}.pkl")
        pkl_dest = f"{save_path}.pkl"
        if os.path.exists(pkl_source):
            shutil.copy2(pkl_source, pkl_dest)
        else:
            print(f"[WARNING] PKL not found: {pkl_source}")

        # Copy ZIP from brain_paths
        zip_source = os.path.join(brain_paths, f"{base_name}.zip")
        zip_dest = f"{save_path}.zip"
        if os.path.exists(zip_source):
            shutil.copy2(zip_source, zip_dest)
        else:
            print(f"[WARNING] ZIP not found: {zip_source}")

        it += 1
        robot_number = 0

    """
    PLOTTING THE RESULTS
    """
    logger.plot_progress_report()

