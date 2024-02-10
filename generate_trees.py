import argparse
from copy import deepcopy
from itertools import product
from treelib import Tree

from config import Config

parser = argparse.ArgumentParser("expression_generator")
parser.add_argument('-c', '--config', help='path to a valid config file', default='default_config.json')
args = parser.parse_args()
config = Config(args.config)

def generate_trees(tree):
    leaves = list(tree.filter_nodes(lambda n: n.is_leaf() and n.data not in config.symbols))
    if len(leaves) == 0:
        yield tree
    else:
        leaf = leaves[0]
        op = leaf.data
        possible_nodes = config.symbols if tree.depth(leaf) == config.max_depth - 1 else config.symbols + config.operations
        if op.is_binary:
            for left, right in product(possible_nodes, repeat=2):
                new_tree = deepcopy(tree)
                new_tree.create_node(str(left), parent=leaf, data=left)
                new_tree.create_node(str(right), parent=leaf, data=right)
                yield from generate_trees(new_tree)
        else:
            for node in possible_nodes:
                new_tree = deepcopy(tree)
                new_tree.create_node(str(node), parent=leaf, data=node)
                yield from generate_trees(new_tree)

def evaluate(tree):
    node = tree[tree.root]
    if node.data in config.symbols:
        return node.data
    op = node.data
    if op.is_binary:
        left, right = tree.children(tree.root)
        return op(evaluate(tree.subtree(left.identifier)), evaluate(tree.subtree(right.identifier)))
    return op(evaluate(tree.subtree(tree.children(tree.root)[0].identifier)))
                
with open('expression_trees.csv', 'w') as file:
    for op in config.operations:
        base_tree = Tree()
        base_tree.create_node(str(op), data=op)
        for tree in generate_trees(base_tree):
            file.write(str(evaluate(tree)))
            # file.write(tree.to_json(sort=False))
            # file.write(str(tree))
            file.write('\n')
        