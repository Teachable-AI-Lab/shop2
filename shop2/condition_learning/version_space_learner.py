from random import choice
import inspect
from itertools import chain
from typing import List, Tuple, Set, Dict, Union
from dataclasses import dataclass
from py_plan.unification import is_variable, unify_var
from py_plan.unification import execute_functions
from py_plan.pattern_matching import build_index, pattern_match
from py_plan.unification import execute_functions, unify
from shop2.fact import Fact
from shop2.conditions import AND, OR, NOT, Filter
from shop2.common import V


class VersionSpaceLearner:
    def __init__(self):
        self.concept = None

    def match(self, instance):
        concept = fact2tuple(self.concept, variables=True)[0]
        instance = fact2tuple(instance, variables=False)[0]
        instance_index = build_index(instance)
        # Find if method's precondition is satisfied for state
        match_substitutions = [m for m in pattern_match(concept, instance_index)]
        if match_substitutions:
            return True
        return False

    def generalize(self):
        pass

    def specialize(self):
        pass


def msubst(theta: Dict, tasks: Union[Task, List, Tuple]) -> Union[Task, List, Tuple]:
    """
    Perform substitutions theta on tasks across the structure (of lists and tuples).
    """
    if isinstance(tasks, Task):
        return Task(*subst(theta, tasks.head))
    else:
        return type(tasks)([msubst(theta, task) for task in tasks])


def subst(s, x):
    if isinstance(x, V):
        return subst(s, f'?{x.name}')
    if x in s:
        return s[x]
    elif isinstance(x, tuple):
        return tuple(subst(s, xi) for xi in x)
    else:
        return x


def unify(x, y, s=(), check=False):
    """
    Unify expressions x and y given a provided mapping (s).  By default s is
    (), which gets recognized and replaced with an empty dictionary. Return a
    mapping (a dict) that will make x and y equal or, if this is not possible,
    then it returns None.

    >>> unify(('Value', '?a', '8'), ('Value', 'cell1', '8'), {})
    {'?a': 'cell1'}

    >>> unify(('Value', '?a', '8'), ('Value', 'cell1', '?b'), {})
    {'?a': 'cell1', '?b': '8'}
    """
    if s == ():
        s = {}

    if s is None:
        return None
    if x == y:
        return s
    if isinstance(x, V):
        return unify_var(f'?{x.name}', y, s, check)
    if isinstance(y, V):
        return unify_var(f'?{y.name}', x, s, check)

    if is_variable(x):
        return unify_var(x, y, s, check)
    if is_variable(y):
        return unify_var(y, x, s, check)

    if (isinstance(x, tuple) and isinstance(y, tuple) and len(x) == len(y)):
        if not x:
            return s
        return unify(x[1:], y[1:], unify(x[0], y[0], s, check), check)
    return None


def fact2tuple(facts, variables=False):
    if isinstance(facts, Fact):
        facts = AND(facts)
    all_tuple_state = list()
    for f in generateLogics(facts):
        tuple_state = set()
        subfacts = flatten([f])
        for fact in subfacts:
            if isinstance(fact, Filter):
                vars = list(inspect.signature(fact.tmpl).parameters.keys())
                tuple_state.add((fact.tmpl, *[f'?{var}' for var in vars]))
                continue
            elif isinstance(fact, NOT):
                for cond in fact[0].conds:
                    value = f'?{cond.value.name}' if isinstance(cond.value, V) else cond.value
                    identifier = f'?{cond.identifier.name}'
                    tuple_state.add(('not', (cond.attribute, identifier, value)))
            else:
                for cond in fact.conds:
                    value = f'?{cond.value.name}' if isinstance(cond.value, V) else cond.value
                    identifier = f'?{cond.identifier.name}' if variables else cond.identifier.name
                    tuple_state.add((cond.attribute, identifier, value))
        all_tuple_state.append(tuple_state)
    return all_tuple_state


def flatten(struct):
    if not isinstance(struct, (list, tuple)) or isinstance(struct, NOT):
        return struct
    # Flatten a list if it contains another list as its element
    if isinstance(struct, list):
        flattened = []
        for item in struct:
            result = flatten(item)
            if isinstance(item, list):
                flattened.extend(result)  # Extend to flatten the list
            else:
                flattened.append(result)
        return flattened

    # Flatten a tuple if it contains another tuple as its element
    elif isinstance(struct, tuple):
        flattened = []
        for item in struct:
            result = flatten(item)
            if isinstance(item, tuple):
                flattened.extend(result)  # Extend to flatten the tuple
            else:
                flattened.append(result)
        return tuple(flattened)

    # Return the structure unchanged if it's neither a list nor a tuple
    return struct


def expandAND(*args):
    # Base case: single element
    if len(args) == 1:
        return [[arg] for arg in args[0]] if isinstance(args[0], list) else [[args[0]]]
    # Recursive case: combine each element of the first argument with the expanded result of the rest
    first, *rest = args
    rest_expanded = expandAND(*rest)
    if isinstance(first, list):
        return [[f] + r for f in first for r in rest_expanded]
    else:
        return [[first] + r for r in rest_expanded]


def expandOR(*args):
    result = []
    for arg in args:
        if isinstance(arg, list):
            result.extend(arg)
        else:
            result.append(arg)
    return result


def generateLogics(expression):
    if isinstance(expression, AND):
        return expandAND(*[generateLogics(arg) for arg in expression])
    elif isinstance(expression, OR):
        return expandOR(*[generateLogics(arg) for arg in expression])
    elif isinstance(expression, NOT):
        return [expression]
    else:
        return expression