from sympy import integrate
from sympy.integrals.risch import NonElementaryIntegral
from sympy.integrals.manualintegrate import integral_steps
from re import finditer

def integral(f, x):
    integral = integrate(f, x, risch=True)
    integral_elementary = True
    integral_rules = set()
    if isinstance(integral, NonElementaryIntegral):
        integral_elementary = False

    if integral_elementary:
        steps = integral_steps(f, x)
        for match in finditer('\w+Rule', str(steps)):
            integral_rules.add(match.group())
        integral = integrate(f, x)

    return {
        'integral': integral,
        'integral_elementary': integral_elementary,
        'integral_rules': list(integral_rules),
    }
