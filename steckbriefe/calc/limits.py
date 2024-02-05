from sympy import S, limit, Limit, oo, FiniteSet, AccumBounds, Symbol, Pow
from sympy.functions.elementary.exponential import log
from sympy.functions.elementary.trigonometric import sec, csc, cot, tan, cos
from operator import itemgetter

from steckbriefe.calc.zeros import zeros

invalid_limit_types = [AccumBounds, Limit]

def limits(f, x=Symbol('x', real=True)):
    limits = {}
    for p in FiniteSet(-oo, oo):
        key = 'limit_inf' if p == oo else 'limit_ninf'
        try:
            l = limit(f, x, p)
            limits[key] = float(l)
        except (TypeError, ValueError, NotImplementedError):
            limits[key] = None
    return limits

def examine_discontinuity(f, x, value):
    s_type = None
    left_limit = limit(f, x, value, '-')
    right_limit = limit(f, x, value, '+')
    if left_limit.is_real and left_limit == right_limit:
        s_type = 'removable'
    elif left_limit.is_real and right_limit.is_real and left_limit != right_limit:
        s_type = 'jump'
    elif any([not l for l in [left_limit, right_limit]]):
        s_type = 'essential'
    elif abs(left_limit) == oo and abs(right_limit) == oo:
        s_type = 'pole'
    if s_type:
        return {
            'value': value,
            'type': s_type,
            'left_limit': left_limit,
            'right_limit': right_limit,
        }
    print('Could not determine type of discontinuity for ', f, value)
    return None

# Code copied and modified from Sympy source code,
# see: https://github.com/sympy/sympy/blob/d2be7bacd2604e98a642f74028e8f0d7d6084f78/sympy/calculus/singularities.py#L27-L104
"""
Copyright (c) 2006-2023 SymPy Development Team

All rights reserved.

Redistribution and use in source and binary forms, with or without
modification, are permitted provided that the following conditions are met:

  a. Redistributions of source code must retain the above copyright notice,
     this list of conditions and the following disclaimer.
  b. Redistributions in binary form must reproduce the above copyright
     notice, this list of conditions and the following disclaimer in the
     documentation and/or other materials provided with the distribution.
  c. Neither the name of SymPy nor the names of its contributors
     may be used to endorse or promote products derived from this software
     without specific prior written permission.


THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
ARE DISCLAIMED. IN NO EVENT SHALL THE REGENTS OR CONTRIBUTORS BE LIABLE FOR
ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT
LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY
OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH
DAMAGE.
"""
def discontinuities(f, x=Symbol('x', real=True)):
    dc = []
    dc_exact = S.EmptySet
    dc_count = 0
    try:
        # log <= 0
        check_expressions = set([i.args[0] for i in f.atoms(log)])
        # division by 0
        for i in f.rewrite([sec, csc, cot, tan], cos).atoms(Pow):
            if i.exp.is_infinite:
                raise NotImplementedError
            if i.exp.is_negative:
                check_expressions.add(i.base)
        
        for expr in check_expressions:
            values, values_exact, count = itemgetter('zeros', 'zeros_exact', 'zeros_count')(zeros(expr, x, throw=True))
            examined = [examine_discontinuity(f, x, value) for value in values]
            filtered = [i for i in examined if i]
            dc += filtered
            if type(count) == int and len(values) != len(filtered):
                count = len(filtered)
            dc_count += count
            dc_exact += values_exact
    except Exception:
        print('discontinuities calculation failed for: ', f)
        dc = []
        dc_exact = None
        dc_count = None

    return {
        'discontinuities': dc,
        'discontinuities_count': dc_count,
        'discontinuities_exact': dc_exact,
    }
