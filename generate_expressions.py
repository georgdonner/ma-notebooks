import re, time
from sympy import sympify, Symbol
from config import Config

config = Config()

def get_constants(fn_str):
    constants_str = list(map(str, config.constants))
    re_constants = re.compile(f"[{''.join(constants_str)}]")
    return re.findall(re_constants, fn_str)

def duplicate_constants(left, right):
    left_consts = left.atoms(Symbol) - set(config.variables)
    right_consts = right.atoms(Symbol) - set(config.variables)
    return left_consts & right_consts

def generate_expressions(sub_expressions):
    for op in config.operations:
        if op.is_binary:
            iterator = op.combinatoric_iterator(sub_expressions)
            for left, right in iterator:
                if config.unique_constants:
                    if len(duplicate_constants(left, right)):
                        continue
                yield op(left, right)
        else:
            for expr in sub_expressions:
                yield op(expr)

def has_prioritized_constants(expr):
    consts = expr.atoms(Symbol) - set(config.variables)
    return consts == set(config.constants[:len(consts)])

def save_expressions(sub_expressions=config.leaf_values, depth=0):
    uniques = set(config.leaf_values)
    if depth < config.max_depth:
        for expr in generate_expressions(sub_expressions):
            if config.allow_constant_expressions or expr.has(*config.variables):
                uniques.add(sympify(expr, evaluate=config.evaluate_expressions))
        save_expressions(sub_expressions=uniques, depth=depth + 1)
    else:
        with open(f'expressions_depth{depth}.csv', 'w') as file:
            for expr in sub_expressions:
                if not config.single_range_constants or has_prioritized_constants(expr):
                    file.write(str(expr) + '\n')

start = time.perf_counter()
save_expressions()
print(time.perf_counter() - start)