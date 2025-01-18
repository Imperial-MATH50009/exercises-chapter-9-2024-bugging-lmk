import numbers
from functools import singledispatch

class Expression:

    def __init__(self, *oper):
        self.operands = oper

    def __add__(self, other):
        if isinstance(other, numbers.Number):
            other = Number(other)

        return Add(self, other)

    def __radd__(self, other):
        if isinstance(other, numbers.Number):
            other = Number(other)

        return other + self

    def __sub__(self, other):
        if isinstance(other, numbers.Number):
            other = Number(other)

        return Sub(self, other)

    def __rsub__(self, other):
        if isinstance(other, numbers.Number):
            other = Number(other)

        return Sub(other, self)

    def __mul__(self, other):
        if isinstance(other, numbers.Number):
            other = Number(other)

        return Mul(self, other)

    def __rmul__(self, other):
        if isinstance(other, numbers.Number):
            other = Number(other)

        return other * self

    def __truediv__(self, other):
        if isinstance(other, numbers.Number):
            other = Number(other)

        return Div(self, other)

    def __rtruediv__(self, other):
        if isinstance(other, numbers.Number):
            other = Number(other)

        return Div(other, self)

    def __pow__(self, other):
        if isinstance(other, numbers.Number):
            other = Number(other)

        return Pow(self, other)

    def __rpow__(self, other):
        if isinstance(other, numbers.Number):
            other = Number(other)

        return Pow(other, self)

#  Terminals


class Terminal(Expression):

    def __init__(self, value, *oper):
        self.value = value
        self.precedence = 0
        super().__init__(*oper)

    def __repr__(self):
        return repr(self.value)

    def __str__(self):
        return str(self.value)


class Number(Terminal):

    def __init__(self, value, *oper):
        if isinstance(value, numbers.Number):
            super().__init__(value, *oper)
        else:
            raise ValueError(f"Number class only takes numbers, not {type(value).__name__}")

    def __repr__(self):
        return super().__repr__()

    def __str__(self):
        return super().__str__()


class Symbol(Terminal):

    def __init__(self, value, *oper):
        if isinstance(value, str):
            super().__init__(value, *oper)
        else:
            raise NotImplementedError(f"Symbol class only takes symbols, not {type(value).__name__}")

    def __repr__(self):
        return super().__repr__()

    def __str__(self):
        return super().__str__()


#  Operators


class Operator(Expression):

    def __init__(self, *oper):
        super().__init__(*oper)

    def __repr__(self):
        return type(self).__name__ + repr(self.operands)

    def __str__(self):
        operands = self.operands
        if all(operands[i].precedence > self.precedence for i in [0, 1]):
            return f"({operands[0]}) {self.symbol} ({operands[1]})"
        elif operands[0].precedence > self.precedence:
            return f"({operands[0]}) {self.symbol} {operands[1]}"
        elif operands[1].precedence > self.precedence:
            return f"{operands[0]} {self.symbol} ({operands[1]})"
        else:
            return f"{operands[0]} {self.symbol} {operands[1]}"


class Add(Operator):

    def __init__(self, *oper):
        self.symbol = "+"
        self.precedence = 3
        super().__init__(*oper)


class Mul(Operator):

    def __init__(self, *oper):
        self.symbol = "*"
        self.precedence = 2
        super().__init__(*oper)


class Sub(Operator):

    def __init__(self, *oper):
        self.symbol = "-"
        self.precedence = 3
        super().__init__(*oper)


class Div(Operator):

    def __init__(self, *oper):
        self.symbol = "/"
        self.precedence = 2
        super().__init__(*oper)


class Pow(Operator):

    def __init__(self, *oper):
        self.symbol = "^"
        self.precedence = 1
        super().__init__(*oper)


#  exercise 2


def postvisitor(expr, visitor, **kwargs):

    stack = []
    visited = {}
    stack += [expr]

    while stack:
        # pop from stack
        e = stack[-1]
        stack.remove(stack[-1])

        unvisited_c = []
        # if o has not been visited at all, add it to unvisited children
        for o in e.operands:
            if o not in visited:
                unvisited_c += [o]

        # if unvisited children, add current node and then unvisited children to the stack in order for them to be evaluated
        if unvisited_c:
            stack += [e]
            stack += unvisited_c
        else:
            visited[e] = visitor(e, *(visited[o] for o in e.operands), **kwargs)

    return visited[expr]


#  exercise 3

@singledispatch
def differentiate(expr, *o, **kwargs):

    raise NotImplementedError(
        f"Cannot evaluate a {type(expr).__name__}")

@differentiate.register(Number)
def _(expr, *o, **kwargs):
    return 0

@differentiate.register(Symbol)
def _(expr, *o, **kwargs):
    if expr in kwargs.values():
        return 1
    else:
        return 0

@differentiate.register(Operator)
def _(expr, *o, **kwargs):
    if o is None:
        return 0
    else:
        return (_(o[0], kwargs) * _(expr, {'var': o[1]})) + (_(o[1], kwargs) * _(expr, {'var': o[1]}))

@differentiate.register(Add)
def _(expr, *o, **kwargs):
    return _(o[0], kwargs) + _(o[1], kwargs)

@differentiate.register(Sub)
def _(expr, *o, **kwargs):
    return _(o[0], kwargs) - _(o[1], kwargs)

@differentiate.register(Mul)
def _(expr, *o, **kwargs):
    return (_(o[0], kwargs) * o[1]) + (_(o[1], kwargs) * o[0])

@differentiate.register(Div)
def _(expr, *o, **kwargs):
    return ((_(o[0], kwargs) * o[1]) - (_(o[1], kwargs) * o[0])) / (o[1] ** 2)

@differentiate.register(Pow)
def _(expr, *o, **kwargs):
    return o[0] * (kwargs ** (o[0] - 1))
