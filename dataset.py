import pandas as pd
from fields import csv_converters

class Dataset:
    def __init__(self, dataframe=None, source='steckbriefe.csv', mode='default'):
        if dataframe is not None:
            self.df = dataframe
        else:
            self.df = pd.read_csv(source, converters=csv_converters(mode=mode))

    #### GENERAL UTILITY FUNCTIONS ####

    def random_function(self):
        if self.df.empty:
            return None
        return self.df.sample(1).to_dict('records')[0]
    
    def exists(self, column, value=True):
        filtered = self.df[self.df[column].notna() if value == True else self.df[column].isna()]
        return Dataset(dataframe=filtered)
    
    def is_equal(self, column, value):
        filtered = self.df[self.df[column] == value]
        return Dataset(dataframe=filtered)
    
    def has(self, column, value):
        exploded = self.df.explode(column)
        filtered = exploded[exploded[column] == value]
        filtered = self.df[self.df.index.isin(filtered.index)]
        return Dataset(dataframe=filtered)
    
    def apply(self, column, fn):
        filtered = self.df[self.df.apply(lambda x: fn(x[column]), axis=1)]
        return Dataset(dataframe=filtered)
    
    def _filter_numerical(self, column, query):
        if type(query) == int or type(query) == float:
            return self.is_equal(column, query)
        elif callable(query):
            return self.apply(column, query)
        else:
            raise TypeError('Unsupported query. Provide integer, float or lambda function.')
    
    #### BASIC PROPERTIES ####

    def polynomial(self, value=True):
        return self.is_equal('polynomial', value)
    
    def rational(self, value=True):
        return self.is_equal('rational', value)
    
    def periodic(self, value=True):
        return self.exists('periodicity', value)
    
    def integral_elementary(self, value=True):
        return self.is_equal('integral_elementary', value)
    
    #### META PROPERTIES ####

    def depth(self, query):
        return self._filter_numerical('depth', query)
    
    def leaves(self, query):
        return self._filter_numerical('leaves', query)
    
    def nodes(self, query):
        return self._filter_numerical('nodes', query)
    
    def max_computation_time(self, seconds):
        return self.apply('computation_seconds', lambda x: x < seconds)
    
    #### EXACT VALUES ####

    def y_intercept(self, query):
        return self._filter_numerical('y_intercept', query)
    
    def limit_infinity(self, query):
        return self._filter_numerical('limit_inf', query)
    
    def limit_negative_infinity(self, query):
        return self._filter_numerical('limit_ninf', query)
    
    def zero(self, value):
        return self.has('zeros', value)
    
    #### COUNTS ####

    def zeros_count(self, query):
        return self._filter_numerical('zeros_count', query)
    
    def asymptotes_count(self, query):
        return self._filter_numerical('asymptotes_count', query)
        
    def singularities_count(self, query):
        return self._filter_numerical('singularities_count', query)
    
    #### OTHER PROPERTIES ####
        
    def integral_rule(self, rule):
        return self.exists('integral').has('integral_rules', rule)

