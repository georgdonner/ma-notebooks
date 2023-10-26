from sympy import *
from sympy.integrals.risch import NonElementaryIntegral
from sympy.integrals.manualintegrate import integral_steps
from operator import itemgetter
import re
import random
import csv

def get_singularities(f, x):
    limits = {}
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
                limits[s] = (left_limit, right_limit)
                if left_limit.is_real and left_limit == right_limit:
                    f_singularities.append((s, 'Hebbare Lücke'))
                elif left_limit.is_real and right_limit.is_real and left_limit != right_limit:
                    f_singularities.append((s, 'Sprungstelle'))
                elif any([not l for l in [left_limit, right_limit]]):
                    f_singularities.append((s, 'Wesentliche Singularität'))
                else:
                    f_singularities.append((s, 'Polstelle'))
                # f_x = f.subs(x, s)
                # if f_x == left_limit:
                #     print('(linksseitig)')
                # elif f_x == right_limit:
                #     print('(rechtsseitig)')
        else:
            singularities_count = oo
            f_singularities = None
    except NotImplementedError:
        pass
    
    return {
        'limits': limits,
        'singularities': f_singularities,
        'singularities_count': singularities_count
    }

def get_limits(f, x):
    limits = {}
    for p in FiniteSet(-oo, oo):
        try:
            l = limit(f, x, p)
            if type(l) != Limit:
                limits[p] = (l)
        except (ValueError, NotImplementedError):
            limits[p] = (None)
    return limits

def get_asymptotes(f, x):
    a = set()
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
            zeros_count = oo
    else:
        zeros = list(zeros_exact)
        zeros_count = len(zeros)

    if zeros_count == oo:
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
    f = sympify(re.sub(r"c(?!o)", lambda m: str(random.choice([1,2,3])), fn_str), locals={'x': x})

    steckbrief = {
        'function': fn_str,
        'function_example': str(f),
    }

    # Definitionsbereich
    steckbrief['domain'] = str(calculus.util.continuous_domain(f, x, S.Reals))

    # Unstetigkeitsstellen
    limits, singularities, singularities_count = itemgetter('limits', 'singularities', 'singularities_count')(get_singularities(f, x))
    steckbrief['singularities'] = singularities
    steckbrief['singularities_count'] = singularities_count

    # Grenzwerte
    steckbrief['limits'] = limits | get_limits(f, x)

    # Asymptoten
    asymptotes = get_asymptotes(f, x)
    steckbrief['asymptotes'] = [str(a) for a in asymptotes]
    steckbrief['asymptotes_count'] = len(asymptotes)

    # Periodizität
    try:
        steckbrief['periodicity'] = periodicity(f, x)
    except RecursionError:
        pass

    # y-Achsenschnitt
    y_intercept = f.subs(x, 0)
    steckbrief['y_intercept'] = y_intercept if y_intercept.is_real else None

    # Nullstellen
    zeros, zeros_count, zeros_exact = itemgetter('zeros', 'zeros_count', 'zeros_exact')(get_zeros(f, x))
    steckbrief['zeros'] = zeros
    steckbrief['zeros_count'] = zeros_count
    steckbrief['zeros_exact'] = str(zeros_exact)

    # Ableitung
    steckbrief['derivative'] = diff(f, x)

    # Integral
    integral, integral_elementary, integral_rules = itemgetter('integral', 'integral_elementary', 'integral_rules')(get_integral(f, x))
    steckbrief['integral'] = str(integral)
    steckbrief['integral_elementary'] = integral_elementary
    steckbrief['integral_rules'] = integral_rules

    return steckbrief

fields = [
    'function', 'function_example', 'domain', 'singularities', 'singularities_count', 'limits', 'asymptotes', 'asymptotes_count', 'periodicity',
    'y_intercept', 'zeros', 'zeros_count', 'zeros_exact', 'derivative', 'integral', 'integral_elementary', 'integral_rules'
]

if __name__ == "__main__":
    depth = 2
    with open(f'uniques_ext_depth{depth}.csv', 'r') as readfile:
        with open(f'steckbriefe{depth}.csv', 'w', newline='', encoding='utf-8') as writefile:
            writer = csv.DictWriter(writefile, fieldnames = fields)
            writer.writeheader()
            i = 0
            for line in readfile:
                line = re.sub('\s+', '', line)
                print(i, line)
                try:
                    steckbrief = main(line)
                    writer.writerow(steckbrief)
                except Exception as e:
                    print(e)
                i += 1
