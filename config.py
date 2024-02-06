import inspect, json, math, operator
from itertools import combinations, combinations_with_replacement, permutations, product
from functools import cached_property
from sympy import symbols, functions, core

op_map = {
    '+': operator.add,
    '-': operator.sub,
    '*': operator.mul,
    '/': operator.truediv,
    '**': operator.pow,
    '^': operator.pow,
    '%': operator.mod,
}

def Sub(a, b, **kwargs):
    return core.Add(a, -b, **kwargs)
def Div(a, b, **kwargs):
    return core.Mul(a, 1/b, **kwargs)

op_map_noeval = {
    '+': core.Add,
    '-': Sub,
    '*': core.Mul,
    '/': Div,
    '**': core.Pow,
    '^': core.Pow,
}

class Operation:
    def __init__(self, operation_str, evaluate=True):
        self.evaluate = evaluate
        self.method = self.parse(operation_str)

    def __call__(self, *args):
        if not self.evaluate:
            return self.method(*args, evaluate=False)
        return self.method(*args)

    def __str__(self):
        return str(self.method)

    def parse(self, operation_str):
        _op_map = op_map if self.evaluate else op_map_noeval
        if operation_str in _op_map:
            return _op_map.get(operation_str)
        if hasattr(operator, operation_str):
            return getattr(operator, operation_str)
        if hasattr(functions, operation_str):
            return getattr(functions, operation_str)
        if hasattr(math, operation_str):
            return getattr(math, operation_str)
        raise ValueError(f'Could not parse operation {operation_str}')
  
    @cached_property
    def is_binary(self):
        signature = inspect.signature(self.method)
        params = [p.name for p in signature.parameters.values() if p.default == inspect.Parameter.empty and p.name != 'kwargs']
        return len(params) == 2 or 'args' in params
  
    @cached_property
    def is_commutative(self):
        a, b = symbols('a b', real=True)
        return self.method(a, b) == self.method(b, a)
  
    @cached_property
    def allow_duplicates(self):
        if self.method == operator.add or self.method == core.Add:
            return False # special case, as x+x = 2*x = c*x, so in the end a duplicate
        a = symbols('a', real=True)
        return not self.method(a, a).is_constant()
    
    def combinatoric_iterator(self, expressions):
        if self.is_commutative and not self.allow_duplicates:
            return combinations(expressions, 2)
        if self.is_commutative:
            return combinations_with_replacement(expressions, 2)
        if not self.allow_duplicates:
            return permutations(expressions, 2)
        return product(expressions, repeat=2)

class Config:
    def __init__(self, filename='default_config.json'):
        with open(filename) as f:
            parsed_config = json.load(f)

            self.max_depth = parsed_config.get('max_depth', 2)
            self.evaluate_expressions = parsed_config.get('evaluate_expressions', True)
            self.allow_constant_expressions = parsed_config.get('allow_constant_expressions', False)
            self.unique_constants = parsed_config.get('unique_constants', False)
            if self.unique_constants:
                self.single_range_constants = parsed_config.get('single_range_constants', False)
            else:
                self.single_range_constants = False

            self.variables = symbols(' '.join(parsed_config.get('variables', ['x'])), real=True, seq=True)
            self.constants = symbols(' '.join(parsed_config.get('constants', ['k'])), real=True, seq=True)

        self.operations = [Operation(op, evaluate=self.evaluate_expressions) for op in parsed_config.get('operations', ['+', '-', '*', '/'])]

    @property
    def symbols(self):
        return list(self.variables + self.constants)
