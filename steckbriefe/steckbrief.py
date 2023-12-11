from sympy import Expr, Set, Symbol, sympify

from steckbriefe.calc.steckbrief import randomize_function
from steckbriefe.fields import all_fields_map

default_param_range = [-5,-4,-3,-2,2,3,4,5]

class Steckbrief:

    def __init__(self, options):
        if type(options) == str:
            self.props = {'function': sympify(options)}
            self.randomize()
        elif type(options) == dict:
            if not 'function' in options:
                raise ValueError("'function' property is required")
            self.props = options
        else:
            raise ValueError("Invalid options supplied. Must either be a (function) string or dict of properties")

    @staticmethod
    def parse_value(value, _type):
        if value == None or isinstance(value, _type) or (_type == Set and isinstance(value, set)):
            return value
        if _type == Expr or _type == Set:
            try:
                return sympify(value)
            except Exception:
                return None
        try:
            return _type(value)
        except TypeError:
            return value
        
    @staticmethod
    def parse_list(value, _type):
        if not value:
            return []
        if isinstance(value, str):
            value = [el for el in value.split(',') if el]
        if isinstance(value, list):
            return [Steckbrief.parse_value(el, _type) for el in value]
        else:
            raise TypeError('Cannot cast value to list')

    @staticmethod
    def parse_prop(prop, value):
        prop_type = all_fields_map[prop]['type']
        if isinstance(prop_type, list):
            return Steckbrief.parse_list(value, prop_type[0])
        return Steckbrief.parse_value(value, prop_type)
    
    def randomize(self, param_range=default_param_range):
        fn = randomize_function(str(self.props['function']), param_range=param_range, sympy_locals={'x': Symbol('x', real=True)})
        self.props['function_example'] = fn

    def get_prop(self, prop):
        if prop in self.props:
            return Steckbrief.parse_prop(prop, self.props[prop])
        if 'calculate' in all_fields_map[prop]:
            calculate_fn = all_fields_map[prop]['calculate']
            self.props.update(calculate_fn(self.function))
        return Steckbrief.parse_prop(prop, self.props[prop])
    
    @property
    def function(self):
        if not 'function_example' in self.props:
            self.randomize()
        return sympify(self.props['function_example'], locals={'x': Symbol('x', real=True)})

    @property
    def depth(self):
        return self.get_prop('depth')
    
    @property
    def leaves(self):
        return self.get_prop('leaves')
    
    @property
    def nodes(self):
        return self.get_prop('nodes')
    
    @property
    def is_polynomial(self):
        return self.get_prop('polynomial')
    
    @property
    def is_rational(self):
        return self.get_prop('rational')
    
    @property
    def domain(self):
        return self.get_prop('domain')
    
    @property
    def function_range(self):
        return self.get_prop('range')
    
    @property
    def singularities(self):
        return self.get_prop('singularities')
    
    @property
    def singularities_count(self):
        return self.get_prop('singularities_count')
    
    @property
    def limit_infinity(self):
        return self.get_prop('limit_inf')
    
    @property
    def limit_negative_infinity(self):
        return self.get_prop('limit_ninf')
    
    @property
    def asymptotes(self):
        return self.get_prop('asymptotes')
    
    @property
    def asymptotes_count(self):
        return self.get_prop('asymptotes_count')
    
    @property
    def periodicity(self):
        return self.get_prop('periodicity')
        
    @property
    def y_intercept(self):
        return self.get_prop('y_intercept')
    
    @property
    def zeros(self):
        return self.get_prop('zeros')
    
    @property
    def zeros_exact(self):
        return self.get_prop('zeros_exact')
    
    @property
    def zeros_count(self):
        return self.get_prop('zeros_count')
    
    @property
    def derivative(self):
        return self.get_prop('derivative')
    
    @property
    def derivative(self):
        return self.get_prop('derivative')
    
    @property
    def minima(self):
        return self.get_prop('minima')
    
    @property
    def maxima(self):
        return self.get_prop('maxima')
    
    @property
    def minima_count(self):
        return self.get_prop('minima_count')
    
    @property
    def maxima_count(self):
        return self.get_prop('maxima_count')
    
    @property
    def integral(self):
        return self.get_prop('integral')
    
    @property
    def is_integral_elementary(self):
        return self.get_prop('integral_elementary')
    
    @property
    def integral_rules(self):
        return self.get_prop('integral_rules')
    