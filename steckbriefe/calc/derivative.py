from sympy import diff, Symbol

def derivative(f, x=Symbol('x', real=True)):
    fd = None
    try:
        fd = diff(f, x)
    except Exception:
        pass
    return {
        'derivative': fd
    }