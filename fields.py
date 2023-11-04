from sympy import parse_expr

all_fields = [
  'function', 'function_example', 'depth', 'leaves', 'polynomial', 'rational', 'domain',
  'singularities', 'singularities_count', 'limit_inf', 'limit_ninf', 'asymptotes', 'asymptotes_count', 
  'periodicity', 'y_intercept', 'zeros', 'zeros_count', 'zeros_exact',
  'derivative', 'integral', 'integral_elementary', 'integral_rules'
]

def parse_sympy(x):
  print(x, type(x))
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
  
def handle_list(list_str, fn):
  if not list_str:
    return []
  return [fn(x) for x in list_str.split(',')]

converters = {
  'y_intercept': parse_number,
  'zeros': lambda x: handle_list(x, parse_number),
  'integral_rules': lambda x: handle_list(x, str),
}

extended_converters = {
  **converters,
  'domain': parse_sympy,
  'zeros_exact': parse_sympy,
}

def csv_converters(mode='basic'):
  if mode == 'extended':
    return extended_converters
  return converters