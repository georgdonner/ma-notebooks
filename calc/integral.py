from sympy import integrate, Integral
from sympy.integrals.risch import NonElementaryIntegral
from sympy.integrals.manualintegrate import integral_steps
from re import finditer

def integral(f, x):
    integral = None
    integral_elementary = True
    integral_rules = set()
    try:
        integral = integrate(f, x, risch=True)
        if len(integral.atoms(NonElementaryIntegral)):
            integral_elementary = False
        if integral_elementary:
            steps = integral_steps(f, x)
            for match in finditer('\w+Rule', str(steps)):
                integral_rules.add(match.group())
            if len(integral.atoms(Integral)) and not 'DontKnowRule' in integral_rules:
                integral = integrate(f, x)
        if 'DontKnowRule' in integral_rules:
            integral_rules = []
        if len(integral.atoms(Integral)):
            integral = None
    except NotImplementedError:
        integral = None
        integral_elementary = None

    return {
        'integral': integral,
        'integral_elementary': integral_elementary,
        'integral_rules': list(integral_rules or []),
    }
