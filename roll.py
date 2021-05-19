import itertools
import random

MAX_D10 = 10
MIN_D10 = 1
MAX_D6 = 6
MIN_D6 = 1
CRIT_COUNT = 2
CRIT_INDEX = CRIT_COUNT - 1

_sysrand = random.SystemRandom()
_randbelow = _sysrand._randbelow


def _gen_check_table():
    fail = []
    success = []
    table = (
        fail,
        *([(i,)] * MAX_D10 for i in range(MIN_D10 + 1, MAX_D10)),
        success,
    )
    for i in range(MIN_D10, MAX_D10 + 1):
        fail.append((MIN_D10, -i))
        success.append((MAX_D10, i))

    return tuple(itertools.chain(*table))


_check_table = _gen_check_table()


def check():
    """roll a check, checks are 1d10 with 1d10 added or subtracted

    returns a list of thrown die results
    """
    return _sysrand.choice(_check_table)


def _gen_d6(permutation, count):
    for _ in range(count):
        yield permutation % MAX_D6 + MIN_D6
        permutation //= MAX_D6


def damage(count):
    """roll damage, damage is the sum of count d6

    two d6 or more landing as 6 would be a critical injury
    returns a list of thrown die results
    """
    if count < 1:
        raise ValueError("count has to be higher than 1")

    permutations = MAX_D6 ** count
    got = _randbelow(permutations)
    return [*_gen_d6(got, count)]


def is_critical(roll):
    """determine if a damage result is a critical injury

    returns True if 2 or more of the values in roll are a 6
    """
    index = 0
    for value in roll:
        if value == MAX_D6:
            if index == CRIT_INDEX:
                return True
            else:
                index += 1

    return False


def sorted_is_critical(roll):
    """same as is_critical but sorts roll

    this is evil because it modifies roll
    """
    roll.sort(reverse=True)
    try:
        return roll[CRIT_INDEX] == MAX_D6
    except IndexError:
        return False
