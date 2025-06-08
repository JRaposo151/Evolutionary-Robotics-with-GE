from sge_FOR_ER.sge.sge import evolutionary_algorithm
from pathlib import Path
from sge_FOR_ER.sge.sge import setup, PPO_train, PPO_TEST
from sge_FOR_ER.sge.sge.parameters import params


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


    def evaluate_robot(self, ROBOT_PATH, name, n_generation, plane):
        """
        Train and evaluate a robot using the given individual
        """

        # Generate a random “fitness” in [0, 1)

        PPO_train.train(ROBOT_PATH, name, n_generation, plane)
        fitness = PPO_TEST.test(ROBOT_PATH, name, plane)


        # Package metadata just like before
        info = {
            'generation_RobotNumber': name,
            'test_fitness': fitness
        }
        print(info)
        return fitness, info

if __name__ == "__main__":
    # Auto-resolve relative to project root
    project_root = Path(__file__).resolve().parents[1]  # up from examples/Test_Robots.py
    param_file = project_root / "parameters" / "standard.yml"

    # path_str = "../parameters/standard.yml"
    # p = Path(path_str)
    if param_file.is_file():
        print(f"\n✔ Found file: {param_file.resolve()}")
    else:
        print(f"\n✘ File not found: {param_file.resolve()}")

    setup(param_file)
    eval_func = BostonHousing(params['RUN'])
    evolutionary_algorithm(evaluation_function=eval_func,
                                              parameters_file=param_file)