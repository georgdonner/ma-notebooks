from sympy import diff, periodicity, Ne, Symbol, S, solveset, ConditionSet
from sympy.sets.sets import EmptySet, imageset, Interval

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

def extrema(f, x=Symbol('x', real=True), fd=None):
    minima = EmptySet()
    maxima = EmptySet()
    inflections = EmptySet()
    fdd = None
    period = None
    try:
        if not fd:
            fd = diff(f, x)
        period = periodicity(fd, x)
        fd_domain = Interval(0, period) if period else S.Reals
        fd_zeros = solveset(fd, x, fd_domain)
        if not fd_zeros.is_empty:
            fdd = diff(fd, x)
            if period:
                fd_minima = solveset(fdd > 0, x, fd_zeros)
                fd_maxima = solveset(fdd < 0, x, fd_zeros)
                for m in fd_maxima:
                    n = Symbol('n')
                    maxima += imageset(n, n*period+m, S.Integers)
                for m in fd_minima:
                    n = Symbol('n')
                    minima += imageset(n, n*period+m, S.Integers)
            else:
                minima = solveset(fdd > 0, x, fd_zeros).simplify()
                maxima = solveset(fdd < 0, x, fd_zeros).simplify()
    except Exception:
        minima = None
        maxima = None

    try:
        if not fdd:
            fdd = diff(f, x)
        fdd_domain = Interval(0, period) if period else S.Reals
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
        'inflections': process_set(inflections),
        'inflections_count': zero_count(inflections),
    }
