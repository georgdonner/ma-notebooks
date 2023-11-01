from sympy import oo, S, Symbol, sympify, calculus, periodicity, diff
from operator import itemgetter
import re, random, csv, time

from calc.meta import tree_props
from calc.limits import limits, singularities
from calc.asymptotes import asymptotes
from calc.zeros import zeros
from calc.integral import integral

def format_list(l):
    if not l:
        return ''
    return ','.join([str(n) for n in l])

def main(fn_str):
    x = Symbol('x', real=True)
    f = sympify(re.sub(r"c(?!o)", lambda m: str(random.choice([2,3,4])), fn_str), locals={'x': x})

    steckbrief = {}
    steckbrief['function_example'] = str(f)
    steckbrief['function'] = fn_str

    # Metainformationen
    depth, leaves = tree_props(f)
    steckbrief['depth'] = depth
    steckbrief['leaves'] = leaves

    # Funktionstyp
    steckbrief['polynomial'] = bool(f.is_polynomial(x))
    steckbrief['rational'] = bool(f.is_rational_function(x))

    # Definitionsbereich
    steckbrief['domain'] = str(calculus.util.continuous_domain(f, x, S.Reals))

    # Unstetigkeitsstellen
    _singularities, singularities_count = itemgetter('singularities', 'singularities_count')(singularities(f, x))
    steckbrief['singularities'] = format_list(_singularities)
    steckbrief['singularities_count'] = singularities_count

    # Grenzwerte
    _limits = limits(f, x)
    steckbrief['limit_inf'] = _limits[oo]
    steckbrief['limit_ninf'] = _limits[-oo]

    # Asymptoten
    _asymptotes = asymptotes(f, x)
    steckbrief['asymptotes'] = format_list(_asymptotes)
    steckbrief['asymptotes_count'] = len(_asymptotes)

    # Periodizität
    try:
        steckbrief['periodicity'] = periodicity(f, x)
    except Exception:
        pass

    # y-Achsenschnitt
    y_intercept = f.subs(x, 0)
    steckbrief['y_intercept'] = y_intercept if y_intercept.is_real else None

    # Nullstellen
    _zeros, zeros_count, zeros_exact = itemgetter('zeros', 'zeros_count', 'zeros_exact')(zeros(f, x))
    steckbrief['zeros'] = format_list(_zeros)
    steckbrief['zeros_count'] = zeros_count
    steckbrief['zeros_exact'] = str(zeros_exact)

    # Ableitung
    steckbrief['derivative'] = diff(f, x)

    # Integral
    _integral, integral_elementary, integral_rules = itemgetter('integral', 'integral_elementary', 'integral_rules')(integral(f, x))
    steckbrief['integral'] = str(_integral)
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
    depth = 1
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
