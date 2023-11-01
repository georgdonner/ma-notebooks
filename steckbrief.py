from sympy import *
from sympy.integrals.risch import NonElementaryIntegral
from sympy.integrals.manualintegrate import integral_steps
from operator import itemgetter
import re, random, csv, math, time

def format_list(l):
    if not l:
        return ''
    return ','.join([str(n) for n in l])

def convert_inf(x):
    if x == oo:
        return math.inf
    if x == -oo:
        return -math.inf
    return x

class ArgStack:
  def __init__(self):
    self.stack = []

  def __len__(self):
    return len([a for a, skip in self.stack if not skip])
  
  def push(self, n_args, skip):
    self.stack.append([n_args, skip])
  
  def pop(self):
    if self.stack[-1][0] <= 1:
      slice_end = 0
      for n, _ in reversed(self.stack):
        if n > 1:
          break
        else:
          slice_end -= 1
      self.stack = self.stack[:slice_end]
    if len(self.stack):
      self.stack[-1][0] -= 1

# this function is needed, because sympy always converts subtraction to addition
# i.e. 1-x to 1+(-1)*x which introduces an extra leaf and level of depth
# it also always converts division to multiplication
# i.e. 4/(1-x) to 4*(1-x)^-1 which also introduces an extra leaf and level of depth
def get_tree_props(f):
  leaves = 0
  arg_stack = ArgStack()
  max_depth = 0
  marked_pows = []
  for expr in preorder_traversal(f):
    skip_depth = False
    if expr.func == Mul:
      arg_types = set([type(a) for a in expr.args])
      # multiplication with -1
      if -1 in expr.args:
        leaves -= 1
        skip_depth = True
      # power of -1 which replaces division (can have multiple in one multiplication)
      if Pow in arg_types:
        # have to mark these pows for later, because you can't retrieve parents of args
        pows = [arg for arg in expr.args if type(arg) == Pow and -1 in arg.args]
        marked_pows += pows
        # a multiplication of -1 and a marked pow in the same expression would reduce leaves and depth too much
        if len(pows) and -1 in expr.args:
          leaves += 1
          skip_depth = False

    if expr.func == Pow and expr in marked_pows:
      leaves -= 1
      skip_depth = True
      marked_pows.remove(expr)
    
    if isinstance(expr, Atom):
      leaves += 1
      arg_stack.pop()
    else:
      arg_stack.push(len(expr.args), skip_depth)

    max_depth = max(max_depth, len(arg_stack))
  return (max_depth, leaves)

def get_singularities(f, x):
    f_singularities = None
    singularities_count = None
    try:
        all_singularities = singularities(f, x, S.Reals)
        if all_singularities.is_FiniteSet:
            f_singularities = []
            singularities_count = len(all_singularities)
            for s in all_singularities:
                left_limit = limit(f, x, s, '-')
                right_limit = limit(f, x, s, '+')
                s_type = 'Polstelle'
                if left_limit.is_real and left_limit == right_limit:
                    s_type = 'Hebbare Lücke'
                elif left_limit.is_real and right_limit.is_real and left_limit != right_limit:
                    s_type = 'Sprungstelle'
                elif any([not l for l in [left_limit, right_limit]]):
                    s_type = 'Wesentliche Singularität'
                f_singularities.append((s, s_type, (left_limit, right_limit)))
        else:
            singularities_count = math.inf
            f_singularities = None
    except NotImplementedError:
        pass
    
    return {
        'singularities': f_singularities,
        'singularities_count': singularities_count
    }

def get_limits(f, x):
    limits = {}
    for p in FiniteSet(-oo, oo):
        try:
            l = limit(f, x, p)
            if type(l) != Limit and not l.as_real_imag()[1]:
                limits[p] = convert_inf(l)
            else:
                limits[p] = None
        except (ValueError, NotImplementedError):
            limits[p] = None
    return limits

def get_asymptotes(f, x):
    a = set()
    if f.is_polynomial(x):
        return a
    for lim in [oo, -oo]:
        try:
            m = limit(f/x, x, lim)
            if m.is_real:
                n = limit(f-m*x, x, lim)
                if n.is_real and n.is_number:
                    a.add(m*x+n)
        except NotImplementedError:
            return []
    return list(a)

def get_zeros(f, x):
    zeros = None
    zeros_count = None
    zeros_exact = solveset(f, x, S.Reals)

    if not zeros_exact.is_FiniteSet:
        if not isinstance(zeros_exact, ConditionSet):
            zeros_count = math.inf
    else:
        zeros = list(zeros_exact)
        zeros_count = len(zeros)

    if zeros_count == math.inf:
        try:
            zeros = [z for z in solve(f, x) if z.is_real]
        except NotImplementedError:
            pass
    return {
        'zeros': zeros,
        'zeros_count': zeros_count,
        'zeros_exact': zeros_exact,
    }

def get_integral(f, x):
    integral = integrate(f, x, risch=True)
    integral_elementary = True
    integral_rules = set()
    if isinstance(integral, NonElementaryIntegral):
        integral_elementary = False

    if integral_elementary:
        steps = integral_steps(f, x)
        for match in re.finditer('\w+Rule', str(steps)):
            integral_rules.add(match.group())
        integral = integrate(f, x)

    return {
        'integral': integral,
        'integral_elementary': integral_elementary,
        'integral_rules': list(integral_rules),
    }

def main(fn_str):
    x = Symbol('x', real=True)
    f = sympify(re.sub(r"c(?!o)", lambda m: str(random.choice([2,3,4])), fn_str), locals={'x': x})

    steckbrief = {}
    steckbrief['function_example'] = str(f)
    steckbrief['function'] = fn_str

    # Metainformationen
    depth, leaves = get_tree_props(f)
    steckbrief['depth'] = depth
    steckbrief['leaves'] = leaves

    # Funktionstyp
    steckbrief['polynomial'] = bool(f.is_polynomial(x))
    steckbrief['rational'] = bool(f.is_rational_function(x))

    # Definitionsbereich
    steckbrief['domain'] = str(calculus.util.continuous_domain(f, x, S.Reals))

    # Unstetigkeitsstellen
    singularities, singularities_count = itemgetter('singularities', 'singularities_count')(get_singularities(f, x))
    steckbrief['singularities'] = format_list(singularities)
    steckbrief['singularities_count'] = singularities_count

    # Grenzwerte
    limits = get_limits(f, x)
    steckbrief['limit_inf'] = limits[oo]
    steckbrief['limit_ninf'] = limits[-oo]

    # Asymptoten
    asymptotes = get_asymptotes(f, x)
    steckbrief['asymptotes'] = format_list(asymptotes)
    steckbrief['asymptotes_count'] = len(asymptotes)

    # Periodizität
    try:
        steckbrief['periodicity'] = periodicity(f, x)
    except Exception:
        pass

    # y-Achsenschnitt
    y_intercept = f.subs(x, 0)
    steckbrief['y_intercept'] = y_intercept if y_intercept.is_real else None

    # Nullstellen
    zeros, zeros_count, zeros_exact = itemgetter('zeros', 'zeros_count', 'zeros_exact')(get_zeros(f, x))
    steckbrief['zeros'] = format_list(zeros)
    steckbrief['zeros_count'] = zeros_count
    steckbrief['zeros_exact'] = str(zeros_exact)

    # Ableitung
    steckbrief['derivative'] = diff(f, x)

    # Integral
    integral, integral_elementary, integral_rules = itemgetter('integral', 'integral_elementary', 'integral_rules')(get_integral(f, x))
    steckbrief['integral'] = str(integral)
    steckbrief['integral_elementary'] = integral_elementary
    steckbrief['integral_rules'] = format_list(integral_rules)

    return steckbrief

fields = [
    'function', 'function_example', 'depth', 'leaves', 'polynomial', 'rational', 'domain',
    'singularities', 'singularities_count', 'limit_inf', 'limit_ninf', 'asymptotes', 'asymptotes_count', 
    'periodicity', 'y_intercept', 'zeros', 'zeros_count', 'zeros_exact',
    'derivative', 'integral','integral_elementary', 'integral_rules'
]

if __name__ == "__main__":
    depth = 2
    start = time.perf_counter()
    with open(f'uniques_ext_depth{depth}.csv', 'r') as readfile:
        with open(f'steckbriefe{depth}.csv', 'w', newline='', encoding='utf-8') as writefile:
            writer = csv.DictWriter(writefile, fieldnames = fields)
            writer.writeheader()
            i = 0
            for line in readfile:
                l_start = time.perf_counter()
                line = re.sub('\s+', '', line)
                try:
                    steckbrief = main(line)
                    writer.writerow(steckbrief)
                except Exception as e:
                    print(e)
                print(i, line, time.perf_counter() - l_start)
                i += 1
    print(f'Took {time.perf_counter() - start} seconds in total')
