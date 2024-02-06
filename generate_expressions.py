import re, time, sys
from sympy import sympify, Symbol, Mul, Function
from config import Config

config = Config(filename='config.json')

def duplicate_constants(left, right):
    left_consts = left.atoms(Symbol) - set(config.variables)
    right_consts = right.atoms(Symbol) - set(config.variables)
    return left_consts & right_consts

def generate_expressions(sub_expressions, reduce_functions=False):
    for op in config.operations:
        if op.is_binary:
            iterator = op.combinatoric_iterator(sub_expressions)
            for left, right in iterator:
                if config.unique_constants:
                    if len(duplicate_constants(left, right)):
                        continue
                if reduce_functions and left.has(Function) and right.has(Function):
                    continue
                yield op(left, right)
        else:
            for expr in sub_expressions:
                if reduce_functions and expr.has(Function):
                    continue
                yield op(expr)

def match_num_mul(expr):
    return expr.is_Mul and any([n.is_number and n != -1 for n in expr.args])
def replace_num_mul(expr):
    return Mul(*[n for n in expr.args if not n.is_number])

def has_prioritized_constants(expr):
    consts = expr.atoms(Symbol) - set(config.variables)
    return consts == set(config.constants[:len(consts)])

def save_expressions(sub_expressions=config.symbols, depth=0):
    uniques = set(config.symbols)
    last_depth = depth == config.max_depth - 1
    if depth < config.max_depth:
        # file = open(f'expressions_depth{depth}reduced4.csv', 'w')
        for expr in generate_expressions(sub_expressions, reduce_functions=True):
            if not config.allow_constant_expressions and not expr.has(*config.variables):
                continue
            expr = sympify(expr, evaluate=config.evaluate_expressions)
            # Eliminate multiplications with symbols
            expr = expr.replace(match_num_mul, replace_num_mul)
            if '1/' in str(expr):
                continue
            uniques.add(expr)
        save_expressions(sub_expressions=uniques, depth=depth + 1)
    else:
        with open(f'expressions_depth{depth}reduced3.csv', 'w') as file:
            for expr in sub_expressions:
                if config.single_range_constants and not has_prioritized_constants(expr):
                    continue
                file.write(str(expr) + '\n')

start = time.perf_counter()
save_expressions()
print(time.perf_counter() - start)