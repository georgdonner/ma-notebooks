import pandas as pd
from steckbriefe.fields import csv_converters
from steckbriefe.steckbrief import Steckbrief

class Dataset:
    def __init__(self, dataframe=None, source='steckbriefe.csv', mode='default'):
        if dataframe is not None:
            self.df = dataframe
        else:
            self.df = pd.read_csv(source, converters=csv_converters(mode=mode))

    #### GENERAL UTILITY FUNCTIONS ####

    def random_steckbrief(self):
        if self.df.empty:
            return None
        return Steckbrief(self.df.sample(1).to_dict('records')[0])
    
    def exists(self, column, value=True):
        filtered = self.df[self.df[column].notna() if value == True else self.df[column].isna()]
        return Dataset(dataframe=filtered)
    
    def is_equal(self, column, value, negate=False):
        included = self.df[column] == value
        filtered = self.df[~included if negate else included]
        return Dataset(dataframe=filtered)
    
    def has(self, column, value, negate=False):
        exploded = self.df.explode(column)
        filtered = exploded[exploded[column] == value]
        included = self.df.index.isin(filtered.index)
        filtered = self.df[~included if negate else included]
        return Dataset(dataframe=filtered)
    
    def apply(self, column, fn):
        filtered = self.df[self.df.apply(lambda x: fn(x[column]), axis=1)]
        return Dataset(dataframe=filtered)
    
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
        return Dataset(dataframe=joined)
    
    #### BASIC PROPERTIES ####

    def is_polynomial(self, value=True):
        return self.is_equal('polynomial', value)
    
    def is_rational(self, value=True):
        return self.is_equal('rational', value)
    
    def is_periodic(self, value=True):
        return self.exists('periodicity', value)
    
    def is_integral_elementary(self, value=True):
        return self.is_equal('integral_elementary', value)
    
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

    def y_intercept(self, query, negate=False):
        return self.filter_numerical('y_intercept', query, negate=negate)
    
    def limit_infinity(self, query, negate=False):
        return self.filter_numerical('limit_inf', query, negate=negate)
    
    def limit_negative_infinity(self, query, negate=False):
        return self.filter_numerical('limit_ninf', query, negate=negate)
    
    def has_zero(self, value, negate=False):
        return self.has('zeros', value, negate=negate)
    
    def has_singularity(self, value, negate=False):
        return self.singularity_prop('value', value, negate=negate)
    
    def has_singularity_type(self, value, negate=False):
        return self.singularity_prop('type', value, negate=negate)
    
    #### COUNTS ####

    def zeros_count(self, query, negate=False):
        return self.filter_numerical('zeros_count', query, negate=negate)
    
    def asymptotes_count(self, query, negate=False):
        return self.filter_numerical('asymptotes_count', query, negate=negate)
        
    def singularities_count(self, query, negate=False):
        return self.filter_numerical('singularities_count', query, negate=negate)
    
    #### OTHER PROPERTIES ####
        
    def integral_rule(self, rule, negate=False):
        return self.exists('integral').has('integral_rules', rule, negate=negate)
    
    #### OTHER UTILS ####
        
    def singularity_prop(self, column, value, negate=False):
        singularity_columns = ['value', 'type', 'left_limit', 'right_limit']
        if not column in singularity_columns:
            raise ValueError('Unsuppored singularity field')
        exploded = self.df.explode('singularities')
        exploded = exploded[exploded['singularities'].notna()]
        exploded[singularity_columns] = exploded['singularities'].apply(pd.Series)
        filtered = exploded[exploded[column] == value]
        included = self.df.index.isin(filtered.index)
        filtered = self.df[~included if negate else included]
        return Dataset(dataframe=filtered)
    