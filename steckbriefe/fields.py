import json
from sympy import parse_expr, Expr, Set

from steckbriefe.calc.meta import tree_props
from steckbriefe.calc.misc import fn_types, periodicity, y_intercept, domain, function_range, inverse, monotonicity, convexity
from steckbriefe.calc.limits import limits, discontinuities
from steckbriefe.calc.asymptotes import asymptotes
from steckbriefe.calc.zeros import zeros
from steckbriefe.calc.integral import integral
from steckbriefe.calc.derivative import derivative, extrema

def parse_sympy(x):
    if x == '':
        return float('nan')
    try:
        return parse_expr(x)
    except ValueError:
        return float('nan')

def parse_number(x):
    try:
        return float(x)
    except ValueError:
        return parse_sympy(x)
    
def parse_discontinuity(discontinuity):
    number_fields = ['value', 'left_limit', 'right_limit']
    return {key: parse_number(val) if key in number_fields else val for key, val in discontinuity.items()}
    
def parse_discontinuity_json(s_json):
    try:
        sings = json.loads(s_json)
        sings = [parse_discontinuity(s) for s in sings]
        return sings
    except Exception as e:
        return [str(e)]
  
def handle_list(list_str, fn):
    if not list_str:
        return []
    return [fn(x) for x in list_str.split(',')]

all_fields_map = {
    'function': {
        'type': Expr,
    },
    'function_example': {
        'type': Expr,
    },
    'depth': {
        'type': int,
        'calculate': tree_props,
    },
    'leaves': {
        'type': int,
        'calculate': tree_props,
    },
    'nodes': {
        'type': int,
        'calculate': tree_props,
    },
    'polynomial': {
        'type': bool,
        'calculate': fn_types,
    },
    'rational': {
        'type': bool,
        'calculate': fn_types,
    },
    'domain': {
        'type': Set,
        'calculate': domain,
        'csv_converter_extended': parse_sympy,
    },
    'range': {
        'type': Set,
        'calculate': function_range,
        'csv_converter_extended': parse_sympy,
    },
    'discontinuities': {
        'type': [dict],
        'calculate': discontinuities,
        'csv_converter': parse_discontinuity_json,
        'api_converter': parse_discontinuity_json
    },
    'discontinuities_count': {
        'type': float,
        'calculate': discontinuities,
    },
    'discontinuities_exact': {
        'type': Set,
        'calculate': discontinuities,
        'csv_converter_extended': parse_sympy,
    },
    'limit_inf': {
        'type': float,
        'calculate': limits,
    },
    'limit_ninf': {
        'type': float,
        'calculate': limits,
    },
    'asymptotes': {
        'type': [Expr],
        'calculate': asymptotes,
        'csv_converter': lambda x: handle_list(x, str),
    },
    'asymptotes_count': {
        'type': float,
        'calculate': asymptotes,
    },
    'periodicity': {
        'type': Expr,
        'calculate': periodicity,
    },
    'y_intercept': {
        'type': Expr,
        'calculate': y_intercept,
        'csv_converter': parse_number,
    },
    'zeros': {
        'type': [Expr],
        'calculate': zeros,
        'csv_converter': lambda x: handle_list(x, parse_number),
    },
    'zeros_count': {
        'type': float,
        'calculate': zeros,
    },
    'zeros_exact': {
        'type': Set,
        'calculate': zeros,
        'csv_converter_extended': parse_sympy,
    },
    'derivative': {
        'type': Expr,
        'calculate': derivative,
    },
    'minima': {
        'type': Set,
        'calculate': extrema,
    },
    'maxima': {
        'type': Set,
        'calculate': extrema,
    },
    'minima_count': {
        'type': float,
        'calculate': extrema,
    },
    'maxima_count': {
        'type': float,
        'calculate': extrema,
    },
    'global_minima': {
        'type': Set,
        'calculate': extrema,
    },
    'global_maxima': {
        'type': Set,
        'calculate': extrema,
    },
    'global_minima_count': {
        'type': float,
        'calculate': extrema,
    },
    'global_maxima_count': {
        'type': float,
        'calculate': extrema,
    },
    'increasing': {
        'type': bool,
        'calculate': monotonicity,
    },
    'decreasing': {
        'type': bool,
        'calculate': monotonicity,
    },
    'convex': {
        'type': bool,
        'calculate': convexity,
    },
    'concave': {
        'type': bool,
        'calculate': convexity,
    },
    'inflections': {
        'type': Set,
        'calculate': extrema,
    },
    'inflections_count': {
        'type': float,
        'calculate': extrema,
    },
    'integral': {
        'type': Expr,
        'calculate': integral,
    },
    'integral_elementary': {
        'type': bool,
        'calculate': integral,
    },
    'integral_rules': {
        'type': [str],
        'calculate': integral,
        'csv_converter': lambda x: handle_list(x, str),
    },
    'inverse': {
        'type': Expr,
        'calculate': inverse,
    },
    'computation_seconds': {
        'type': float,
    },
}

all_fields = all_fields_map.keys()

converters = {key:field['csv_converter'] for key, field in all_fields_map.items() if 'csv_converter' in field}
extended_converters = {key:field['csv_converter_extended'] for key, field in all_fields_map.items() if 'csv_converter_extended' in field}
extended_converters = {
    **converters,
    **extended_converters,
}

def csv_converters(mode='default'):
    if mode == 'extended':
        return extended_converters
    return converters
