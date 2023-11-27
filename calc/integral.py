from sympy import integrate, Integral
from sympy.integrals.risch import NonElementaryIntegral
from sympy.integrals.manualintegrate import integral_steps

valid_attrs = ['substep', 'substeps', 'v_step', 'second_step', 'alternatives']
ignore_rules = ['AlternativeRule']

def get_rule(step):
    rule = type(step).__name__
    if rule not in ignore_rules:
        yield rule
    for attr in valid_attrs:
        if hasattr(step, attr):
            if attr == 'alternatives':
                yield from get_rule(step.alternatives[0])
            elif attr == 'substeps':
                for substep in step.substeps:
                    yield from get_rule(substep)
            else:
                yield from get_rule(getattr(step, attr))

def get_rules(steps):
    return list(dict.fromkeys((get_rule(steps))))

def integral(f, x):
    integral = None
    integral_elementary = True
    integral_rules = []
    try:
        integral = integrate(f, x, risch=True)
        if len(integral.atoms(NonElementaryIntegral)):
            integral_elementary = False
        if integral_elementary:
            steps = integral_steps(f, x)
            integral_rules = get_rules(steps)
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
        'integral_rules': integral_rules,
    }
