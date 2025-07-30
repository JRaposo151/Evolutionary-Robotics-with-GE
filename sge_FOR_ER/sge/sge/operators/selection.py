import random
import copy


def tournament(population, tsize=3):
    pool = random.sample(population, tsize)
    pool.sort(key=lambda i: i['fitness'], reverse=True)
    return copy.deepcopy(pool[0])
