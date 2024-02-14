import argparse, re
import pandas as pd
from steckbriefe.fields import parse_discontinuity_json, csv_dtypes, handle_list

parser = argparse.ArgumentParser("reduce_csv")
parser.add_argument('input', help='input csv file with steckbriefe')
parser.add_argument('-f', '--format', help='output file format', default='pickle', type=str, choices=['pickle', 'csv'])
parser.add_argument('-o', '--output', help='output file for steckbriefe', type=str)
args = parser.parse_args()
if not args.output:
    args.output = 'reduced_' + re.sub(r'\w+$', args.format, args.input)

dtypes = csv_dtypes()
csv_converters = {
    'discontinuities': parse_discontinuity_json,
    'integral_rules': lambda x: handle_list(x, str),
}
# only check existence for SymPy fields
check_exist = ['domain', 'range', 'periodicity', 'zeros_exact', 'derivative', 'integral', 'inverse']
for field in check_exist:
    csv_converters[field] = lambda val: bool(val)

df = pd.read_csv(args.input, dtype=dtypes, converters=csv_converters)
# Expand integral rules
df = df.join(df['integral_rules'].str.join(',').str.get_dummies(sep=',').astype(bool))
# Expand discontinuity types
df['disc_types'] = df['discontinuities'].apply(lambda arr: [d['type'] for d in arr])
df = df.join(df['disc_types'].str.join(',').str.get_dummies(sep=',').astype(bool))
# Retain function examples
function_col = df['function_example']
# Only include easily indexable values like numbers and booleans
reduced = df.select_dtypes(exclude=['object'])
reduced.insert(loc=0, column='function_example', value=function_col)
reduced = reduced.rename(columns={'zeros_exact': 'zeros'})

if args.format == 'csv':
    reduced.to_csv(args.output)
elif args.format == 'pickle':
    reduced.to_pickle(args.output)
