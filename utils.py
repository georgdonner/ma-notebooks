from sympy import oo
from math import inf

def convert_inf(x):
    if x == oo:
        return inf
    if x == -oo:
        return -inf
    return x
