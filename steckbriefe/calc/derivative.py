from sympy import diff, Ne, Symbol, S, solveset, ConditionSet
from sympy.calculus.util import periodicity, function_range, continuous_domain
from sympy.sets.sets import EmptySet, FiniteSet, imageset, Interval

from steckbriefe.calc.zeros import zero_count

def derivative(f, x=Symbol('x', real=True)):
    fd = None
    try:
        fd = diff(f, x)
    except Exception:
        pass
    return {
        'derivative': fd
    }

def process_set(_set):
    if isinstance(_set, ConditionSet) or isinstance(_set, EmptySet):
        return None
    return _set

def extrema(f, x=Symbol('x', real=True), domain=None, fd=None, fn_range=None):
    minima = EmptySet()
    maxima = EmptySet()
    global_minima = EmptySet()
    global_maxima = EmptySet()
    inflections = EmptySet()
    fdd = None
    period = None
    try:
        if not fd:
            fd = diff(f, x)
        if not fn_range:
            fn_range = function_range(f, x, S.Reals)
        if not domain:
            domain = continuous_domain(f, x, S.Reals)
        period = periodicity(fd, x)
        fd_domain = Interval(0, period) if period else domain
        fd_zeros = solveset(fd, x, fd_domain)
        if not fd_zeros.is_empty:
            fdd = diff(fd, x)
            if period:
                fd_minima = solveset(fdd > 0, x, fd_zeros)
                fd_maxima = solveset(fdd < 0, x, fd_zeros)
                n = Symbol('n')
                for m in fd_minima:
                    min_periodic = imageset(n, n*period+m, S.Integers)
                    minima += min_periodic
                    if fn_range and f.subs(x, m) == fn_range.inf:
                        global_minima += min_periodic
                for m in fd_maxima:
                    max_periodic = imageset(n, n*period+m, S.Integers)
                    maxima += max_periodic
                    if fn_range and f.subs(x, m) == fn_range.sup:
                        global_maxima += max_periodic
            else:
                minima = solveset(fdd > 0, x, fd_zeros).simplify()
                if fn_range and minima.is_FiniteSet:
                    global_minima += FiniteSet(*[m for m in minima if f.subs(x, m) == fn_range.inf])
                maxima = solveset(fdd < 0, x, fd_zeros).simplify()
                if fn_range and maxima.is_FiniteSet:
                    global_maxima += FiniteSet(*[m for m in maxima if f.subs(x, m) == fn_range.sup])
    except Exception:
        minima = None
        maxima = None

    if not fn_range:
        global_minima = None
        global_maxima = None

    try:
        if not fdd:
            fdd = diff(f, x)
        fdd_domain = Interval(0, period) if period else domain
        fdd_zeros = solveset(fdd, x, fdd_domain)
        if not fdd_zeros.is_empty:
            fddd = diff(fdd, x)
            if period:
                for i in solveset(Ne(fddd, 0), x, fdd_zeros):
                    n = Symbol('n')
                    inflections += imageset(n, n*period+i, S.Integers)
            else:
                inflections = solveset(Ne(fddd, 0), x, fdd_zeros).simplify()
    except Exception:
        inflections = None

    return {
        'minima': process_set(minima),
        'maxima': process_set(maxima),
        'minima_count': zero_count(minima),
        'maxima_count': zero_count(maxima),
        'global_minima': process_set(global_minima),
        'global_maxima': process_set(global_maxima),
        'global_minima_count': zero_count(global_minima),
        'global_maxima_count': zero_count(global_maxima),
        'inflections': process_set(inflections),
        'inflections_count': zero_count(inflections),
    }
