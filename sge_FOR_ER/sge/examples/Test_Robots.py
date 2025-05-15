import random
import sge_FOR_ER
from pathlib import Path
from sge_FOR_ER.sge.sge import setup
from sge_FOR_ER.sge.sge.parameters import params
from sge_FOR_ER.sge.sge.utilities.protected_math import _log_, _div_, _exp_, _inv_, _sqrt_, protdiv
from numpy import cos, sin


def drange(start, stop, step):
    r = start
    while r < stop:
        yield r
        r += step


class BostonHousing():
    def __init__(self, run=0, has_test_set=True, invalid_fitness=9999999):
        self.__train_set = []
        self.__test_set = None
        self.__invalid_fitness = invalid_fitness
        self.run = run
        self.has_test_set = has_test_set


    def evaluate_robot(self, ROBOT_PATH, name):
        """
        Train and evaluate a robot using the given individual
        """
        from Controller import PPO_train, PPO_TEST
        # Generate a random “fitness” in [0, 1)
        PPO_train.train(ROBOT_PATH,name)
        fitness = PPO_TEST.test(ROBOT_PATH, name)
        # Package metadata just like before
        info = {
            'generation_RobotNumber': name,
            'test_fitness': fitness
        }
        return fitness, info

if __name__ == "__main__":
    path_str = "../parameters/standard.yml"
    p = Path(path_str)
    if p.is_file():
        print(f"✔ Found file: {p.resolve()}")
    else:
        print(f"✘ File not found: {p.resolve()}")

    setup("../parameters/standard.yml")
    eval_func = BostonHousing(params['RUN'])
    sge_FOR_ER.sge.sge.evolutionary_algorithm(evaluation_function=eval_func,
                                              parameters_file="../parameters/standard.yml")