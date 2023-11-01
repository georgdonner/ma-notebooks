from sympy import Atom, Mul, Pow, preorder_traversal

class ArgStack:
    def __init__(self):
      self.stack = []

    def __len__(self):
        return len([a for a, skip in self.stack if not skip])
  
    def push(self, n_args, skip):
        self.stack.append([n_args, skip])
  
    def pop(self):
        if not len(self.stack):
            return
        if self.stack[-1][0] <= 1:
            slice_end = 0
            for n, _ in reversed(self.stack):
                if n > 1:
                    break
                else:
                    slice_end -= 1
            self.stack = self.stack[:slice_end]
            if len(self.stack):
                self.stack[-1][0] -= 1

# this function is needed, because sympy always converts subtraction to addition
# i.e. 1-x to 1+(-1)*x which introduces an extra leaf and level of depth
# it also always converts division to multiplication
# i.e. 4/(1-x) to 4*(1-x)^-1 which also introduces an extra leaf and level of depth
def tree_props(f):
    leaves = 0
    arg_stack = ArgStack()
    max_depth = 0
    marked_pows = []
    for expr in preorder_traversal(f):
        skip_depth = False
        if expr.func == Mul:
            arg_types = set([type(a) for a in expr.args])
            # multiplication with -1
            if -1 in expr.args:
                leaves -= 1
                skip_depth = True
            # power of -1 which replaces division (can have multiple in one multiplication)
            if Pow in arg_types:
                # have to mark these pows for later, because you can't retrieve parents of args
                pows = [arg for arg in expr.args if type(arg) == Pow and -1 in arg.args]
                marked_pows += pows
                # a multiplication of -1 and a marked pow in the same expression would reduce leaves and depth too much
                if len(pows) and -1 in expr.args:
                    leaves += 1
                    skip_depth = False

        if expr.func == Pow and expr in marked_pows:
            leaves -= 1
            skip_depth = True
            marked_pows.remove(expr)
        
        if isinstance(expr, Atom):
            leaves += 1
            arg_stack.pop()
        else:
            arg_stack.push(len(expr.args), skip_depth)

        max_depth = max(max_depth, len(arg_stack))
    return (max_depth, leaves)

