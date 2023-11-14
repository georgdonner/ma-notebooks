from operator import itemgetter
import re, random, csv, time
from sympy import oo, S, Symbol, sympify, calculus, periodicity, diff
from concurrent.futures import TimeoutError
import multiprocessing as mp
from pebble import ProcessPool

from calc.meta import tree_props
from calc.limits import limits, singularities
from calc.asymptotes import asymptotes
from calc.zeros import zeros
from calc.integral import integral
from fields import all_fields

def format_list(l):
    if not l:
        return ''
    return ','.join([str(n) for n in l])

def has_inverse_trig(fn_str):
    return 'asin' in fn_str or 'acos' in fn_str

def main(fn_str, queue):
    x = Symbol('x', real=True)
    f = sympify(re.sub(r"k", lambda _: str(random.choice([2,3,4])), fn_str), locals={'x': x})

    start = time.perf_counter()

    steckbrief = {}
    steckbrief['function_example'] = str(f)
    steckbrief['function'] = fn_str

    # Metainformationen
    depth, leaves, nodes = tree_props(f)
    steckbrief['depth'] = depth
    steckbrief['leaves'] = leaves
    steckbrief['nodes'] = nodes

    # Funktionstyp
    steckbrief['polynomial'] = bool(f.is_polynomial(x))
    steckbrief['rational'] = bool(f.is_rational_function(x))

    # Definitionsbereich
    domain = None
    if not has_inverse_trig(fn_str):
        # sympy returns wrong results for inverse trigonometric functions, see https://github.com/sympy/sympy/issues/21786
        try:
            domain = calculus.util.continuous_domain(f, x, S.Reals)
        except Exception:
            pass
    steckbrief['domain'] = str(domain) if domain else domain

    # Wertebereich
    f_range = None
    if not has_inverse_trig(fn_str):
        try:
            f_range = calculus.util.function_range(f, x, domain or S.Reals)
        except Exception:
            pass
    steckbrief['range'] = str(f_range) if f_range else f_range

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
    try:
        y_intercept = f.subs(x, 0)
        steckbrief['y_intercept'] = y_intercept if y_intercept.is_real else None
    except Exception:
        pass

    # Nullstellen
    _zeros, zeros_count, zeros_exact = itemgetter('zeros', 'zeros_count', 'zeros_exact')(zeros(f, x, domain or S.Reals))
    steckbrief['zeros'] = format_list(_zeros)
    steckbrief['zeros_count'] = zeros_count
    steckbrief['zeros_exact'] = str(zeros_exact)

    # Ableitung
    try:
        steckbrief['derivative'] = diff(f, x)
    except Exception:
        pass

    # Integral
    _integral, integral_elementary, integral_rules = itemgetter('integral', 'integral_elementary', 'integral_rules')(integral(f, x))
    steckbrief['integral'] = _integral
    steckbrief['integral_elementary'] = integral_elementary
    steckbrief['integral_rules'] = format_list(integral_rules)

    print(fn_str, time.perf_counter() - start)

    queue.put(steckbrief)

    return steckbrief

def queue_listener(queue, filename):
    with open(filename, 'a', newline='', encoding='utf-8') as file:
        while True:
            payload = queue.get()
            writer = csv.DictWriter(file, fieldnames = all_fields)
            writer.writerow(payload)
            file.flush()

def done(future):
    try:
        future.result()
    except TimeoutError as error:
        print('Function timed out')
    except Exception as error:
        print('Function raised %s' % error)
        print(error.traceback)

if __name__ == "__main__":
    timeout = 30
    depth = 2
    write_filename = f'steckbriefe{depth}.csv'
    start = time.perf_counter()

    manager = mp.Manager()
    queue = manager.Queue()
    queue_process = mp.Process(target=queue_listener, args=(queue, write_filename))
    queue_process.start()

    with open(write_filename, 'w', newline='') as writefile:
        writer = csv.DictWriter(writefile, fieldnames = all_fields)
        writer.writeheader()

    with ProcessPool() as pool:
        with open(f'uniques_ext_depth{depth}.csv', 'r') as readfile:
            for line in readfile:
                if line != 'k':
                    line = re.sub('\s+', '', line)
                    future = pool.schedule(main, (line, queue), timeout=timeout)
                    future.add_done_callback(done)
        pool.close()
        pool.join()
        queue_process.kill()

    print(f'Took {time.perf_counter() - start} seconds in total')
