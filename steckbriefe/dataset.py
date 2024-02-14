from functools import wraps
from io import StringIO
import pandas as pd
from steckbriefe.fields import csv_converters, csv_dtypes
from steckbriefe.steckbrief import Steckbrief

def not_external(fn):
    @wraps(fn)
    def decorated(*args, **kwargs):
        if args[0].external_source:
            raise ValueError('method not supported with external source')
        return fn(*args, **kwargs)
    return decorated

class Dataset:
    def __init__(self, dataframe=None, source='steckbriefe_depth2.csv', external_source=None, mode='default'):
        if dataframe is not None:
            self.df = dataframe
        else:
            if source.endswith('csv'):
                converters = None if external_source else csv_converters(mode=mode)
                self.df = pd.read_csv(source, converters=converters, dtype=csv_dtypes())
            elif source.endswith('pickle'):
                self.df = pd.read_pickle(source)
            else:
                raise ValueError('unsupported source type')
        self.external_source = external_source

    #### GENERAL UTILITY FUNCTIONS ####

    def random_steckbrief(self):
        if self.df.empty:
            return None
        sampled = self.df.sample(1)
        if self.external_source:
            index = sampled.index.astype(int)[0]
            csv_string = ''
            with open(self.external_source, 'r') as f:
                for i, line in enumerate(f):
                    if i == 0:
                        csv_string += line
                    elif i == index + 1:
                        csv_string += line
                        break
            sampled = pd.read_csv(StringIO(csv_string), converters=csv_converters(mode='extended'), dtype=csv_dtypes())
        return Steckbrief(sampled.to_dict('records')[0])
    
    def exists(self, column, value=True):
        filtered = self.df[self.df[column].notna() if value == True else self.df[column].isna()]
        return Dataset(dataframe=filtered, external_source=self.external_source)
    
    def is_equal(self, column, value, negate=False):
        included = self.df[column] == value
        filtered = self.df[~included if negate else included]
        return Dataset(dataframe=filtered, external_source=self.external_source)
    
    def has(self, column, value, negate=False):
        if self.external_source:
            return self.is_equal(value, True, negate=negate)
        exploded = self.df.explode(column)
        filtered = exploded[exploded[column] == value]
        included = self.df.index.isin(filtered.index)
        filtered = self.df[~included if negate else included]
        return Dataset(dataframe=filtered, external_source=self.external_source)
    
    def apply(self, column, fn):
        filtered = self.df[self.df.apply(lambda x: fn(x[column]), axis=1)]
        return Dataset(dataframe=filtered, external_source=self.external_source)
    
    def filter_numerical(self, column, query, negate=False):
        if type(query) == int or type(query) == float:
            return self.is_equal(column, query, negate=negate)
        elif callable(query):
            return self.apply(column, query)
        else:
            raise TypeError('Unsupported query. Provide integer, float or lambda function.')
        
    def join(self, dataset):
        joined = pd.concat([self.df, dataset.df])
        joined = joined[~joined.index.duplicated()]
        return Dataset(dataframe=joined, external_source=self.external_source)
    
    #### BASIC PROPERTIES ####

    @not_external
    def domain_reals(self, value=True):
        return self.apply('domain', lambda val: str(val) == 'Reals' if value else str(val) != 'Reals')

    @not_external
    def range_reals(self, value=True):
        return self.apply('range', lambda val: str(val) == 'Reals' if value else str(val) != 'Reals')

    def is_polynomial(self, value=True):
        return self.is_equal('polynomial', value)
    
    def is_rational(self, value=True):
        return self.is_equal('rational', value)
    
    def is_periodic(self, value=True):
        return self.exists('periodicity', value)
    
    def is_integral_elementary(self, value=True):
        return self.is_equal('integral_elementary', value)
    
    def is_increasing(self, value=True):
        return self.is_equal('increasing', value)
    
    def is_decreasing(self, value=True):
        return self.is_equal('decreasing', value)
    
    def is_convex(self, value=True):
        return self.is_equal('convex', value)
    
    def is_concave(self, value=True):
        return self.is_equal('concave', value)
    
    #### META PROPERTIES ####

    def depth(self, query, negate=False):
        return self.filter_numerical('depth', query, negate=negate)
    
    def leaves(self, query, negate=False):
        return self.filter_numerical('leaves', query, negate=negate)
    
    def nodes(self, query, negate=False):
        return self.filter_numerical('nodes', query, negate=negate)
    
    def max_computation_time(self, seconds):
        return self.apply('computation_seconds', lambda x: x < seconds)
    
    #### EXACT VALUES ####

    @not_external
    def y_intercept(self, query, negate=False):
        return self.filter_numerical('y_intercept', query, negate=negate)
    
    @not_external
    def limit_infinity(self, query, negate=False):
        return self.filter_numerical('limit_inf', query, negate=negate)
    
    @not_external
    def limit_negative_infinity(self, query, negate=False):
        return self.filter_numerical('limit_ninf', query, negate=negate)
    
    @not_external
    def has_zero(self, value, negate=False):
        return self.has('zeros', value, negate=negate)
    
    @not_external
    def has_discontinuity(self, value, negate=False):
        return self.discontinuity_prop('value', value, negate=negate)
    
    def has_discontinuity_type(self, value, negate=False):
        if self.external_source:
            return self.is_equal(value, True, negate=negate)
        return self.discontinuity_prop('type', value, negate=negate)
    
    #### COUNTS ####

    def zeros_count(self, query, negate=False):
        return self.filter_numerical('zeros_count', query, negate=negate)
    
    def asymptotes_count(self, query, negate=False):
        return self.filter_numerical('asymptotes_count', query, negate=negate)
        
    def discontinuities_count(self, query, negate=False):
        return self.filter_numerical('discontinuities_count', query, negate=negate)
        
    def minima_count(self, query, global_only=False, negate=False):
        field = ('global_' if global_only else '') + 'minima_count'
        return self.filter_numerical(field, query, negate=negate)
        
    def maxima_count(self, query, global_only=False, negate=False):
        field = ('global_' if global_only else '') + 'maxima_count'
        return self.filter_numerical(field, query, negate=negate)
        
    def inflections_count(self, query, negate=False):
        return self.filter_numerical('inflections_count', query, negate=negate)
    
    #### OTHER PROPERTIES ####
        
    def integral_rule(self, rule, negate=False):
        return self.exists('integral').has('integral_rules', rule, negate=negate)
    
    #### OTHER UTILS ####
        
    def discontinuity_prop(self, column, value, negate=False):
        discontinuity_columns = ['value', 'type', 'left_limit', 'right_limit']
        if not column in discontinuity_columns:
            raise ValueError('Unsuppored discontinuity field')
        exploded = self.df.explode('discontinuities')
        exploded = exploded[exploded['discontinuities'].notna()]
        exploded[discontinuity_columns] = exploded['discontinuities'].apply(pd.Series)
        filtered = exploded[exploded[column] == value]
        included = self.df.index.isin(filtered.index)
        filtered = self.df[~included if negate else included]
        return Dataset(dataframe=filtered, external_source=self.external_source)
    