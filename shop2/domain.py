from random import choice
from collections import defaultdict
import inspect
from itertools import chain
from typing import List, Tuple, Set, Dict, Union
from uuid import uuid4
from dataclasses import dataclass
from py_plan.unification import is_variable, unify_var
from py_plan.unification import execute_functions
from py_plan.pattern_matching import build_index, pattern_match
from py_plan.unification import unify
from shop2.fact import Fact
from shop2.conditions import AND, OR, NOT, Filter
from shop2.common import V


class Axiom:
    """
    As defined for Axiom in domain description of SHOP2
    """   
    def __init__(self, head, conditions=list()):
        self.head = head
        self.name = head[0]
        self.conditions = set(conditions)

    def applicable(self, state):
        index = build_index(state)
        for theta in pattern_match(self.conditions, index): # Find if axiom's precondition is satisfied for state
            state.add(subst(theta, self.head))
        return state

    def __str__(self):
        s = f"Name: {self.name}\n"
        s += f"Conditions: {self.conditions}\n"
        return s

    def __repr__(self):
        return f"<Axiom {self.name}>" 


class Method:
    """
    As defined for Method in domain description of SHOP2
    """
    def __init__(self, head, preconditions, subtasks, unless_conditions=(), cost=1):
        self.id = str(uuid4()).replace('-', '')
        self.head = head
        self.name = head[0]
        self.args = head[1:]
        self.preconditions = preconditions
        self.unless_conditions = unless_conditions
        self.subtasks = subtasks
        # TODO cost = sum of costs of operators in subtasks
        self.cost = cost

    def applicable(self, task, state, plan, visited):
        # ptstate = fact2tuple(state, variables=False)[0]
        ptstate = dict_to_tuple(state)
        index = build_index(ptstate)
        substitutions = unify(task.head, self.head)
        if not self.preconditions:
            return msubst(substitutions, self.subtasks)
        ptconditions = fact2tuple(self.preconditions, variables=True)
        for ptcondition in ptconditions:
            if (task.name, str(ptcondition), str(state), plan) in visited:
                continue
            visited.append((task.name, str(ptcondition), str(state), plan))
            # Find if method's precondition is satisfied by state
            # Only checks one substitution, not all
            methods = [(self.name, theta) for theta in pattern_match(ptcondition, index, substitutions)]
            if methods:
                m, theta = choice(methods)
                return {
                    'option_type': 'method',
                    'id': self.name,
                    'name': self.name,
                    'grounded_subtasks': msubst(theta, self.subtasks),
                    'matched_facts': tuples_to_dicts(subst(theta, tuple(ptcondition)),
                                                     use_facts=True, use_and_operator=True)
                }
                # return msubst(theta, self.subtasks)

        return False

    def __str__(self):
        s = f"Name: {self.name}\n"
        s += f"Preconditions: {self.preconditions}\n"
        s += f"Subtasks: {self.subtasks}\n"
        return s

    def __repr__(self):
        return f"<Method {self.name}>" 


class Operator:
    """
    As defined for Operator in domain description of SHOP2
    """
    def __init__(self, head, preconditions, effects, unless_conditions=(), cost=1):
        self.id = str(uuid4()).replace('-', '')
        self.head = head
        self.name = head[0]
        self.args = head[1:]
        self.preconditions = preconditions
        self.unless_conditions = unless_conditions
        self.effects = effects
        self.cost = cost

        self.add_effects = set()
        self.del_effects = set()

        if isinstance(self.effects, Fact):
            self.add_effects.add(self.effects)
        elif isinstance(self.effects, NOT):
            self.del_effects.add(self.effects[0])
        else:     
            for e in self.effects:
                if isinstance(e, NOT):
                    self.del_effects.add(e[0])
                else:
                    self.add_effects.add(e)

    def applicable(self, task, state):
        # ptstate = fact2tuple(state, variables=False)[0]
        ptstate = dict_to_tuple(state)
        index = build_index(ptstate)        
        substitutions = unify(task.head, self.head)
        if not self.preconditions:
            grounded_args = tuple([substitutions[f'?{v.name}'] for v in self.args if f'?{v.name}' in substitutions])
            return self.name, grounded_args, self.get_effects(substitutions)
        ptconditions = fact2tuple(self.preconditions, variables=True)
        for ptcondition in ptconditions:
            actions = [(self.name, theta) for theta in pattern_match(ptcondition, index, substitutions)]
            if actions:
                a, theta = choice(actions)
                grounded_args = tuple([theta[f'?{v.name}'] for v in self.args if f'?{v.name}' in theta])
                return {
                    'option_type': 'method',
                    'id': self.name,
                    'name': self.name,
                    'grounded_arguments': grounded_args,
                    'matched_facts': tuples_to_dicts(subst(theta, tuple(ptcondition)),
                                                     use_facts=True, use_and_operator=True),
                    'effects': self.get_effects(theta)
                    }
        return False

    def get_effects(self, theta):
        add_effects, del_effects = set(), set()
        for effect in self.add_effects:
            add_effects.add(effect.duplicate())
        for effect in self.del_effects:
            del_effects.add(effect.duplicate())

        all_effects = []
        for effect in chain(add_effects, del_effects):
            # print(effect)
            for cond in effect.conds:
                # print('cond: ', cond)
                if isinstance(cond.value, tuple) and callable(cond.value[0]):
                    cond.value = tuple([f'?{x.name}' if isinstance(x, V) else x for x in cond.value])
                effect[cond.attribute] = execute_functions(cond.value, theta) if not isinstance(cond.value, V) \
                    else subst(theta, cond.value)
            all_effects.append({k: effect[k] for k in effect})
        # return add_effects, delete_effects
        return all_effects
    
    def __str__(self):
        s = f"Name: {self.name}\n"
        s += f"Preconditions: {self.preconditions}\n"
        s += f"Effects: {self.effects}\n"
        return s

    def __repr__(self):
        return f"<Operator {self.name}>"


class Task:
    def __init__(self, name: str,
                 args: Union[Union[List[Union[str, 'V']], Tuple[Union[str, 'V']]]] = (),
                 priority: int = 1,
                 repeat: bool = False):
        self.id = str(uuid4()).replace('-', '')
        self.name = name
        self.args = args
        self.head = (self.name, *self.args)
        # index_chain keeps track of where task is in global task list for easier removal
        self.index_chain = None
        # Convert priority value if necessary
        priority_map = {'first': 0, 'high': 1, 'medium': 2, 'low': 3}
        self.priority = priority_map[priority] \
            if priority in priority_map else priority
        self.repeat = repeat if repeat is not None else False

    # def head(self):
    #     return self.name, *self.args

    def __copy__(self):
        return self._copy()

    def __deepcopy__(self, memodict={}):
        return self._copy()

    def __str__(self):
        return self._get_str()

    def __repr__(self):
        return self._get_str()

    def _get_str(self):
        s = f"Task({self.name}"
        if self.args:
            for a in self.args:
                s += f", {a}"
        s += ")"
        return s

    def _copy(self):
        new_task = Task(self.name, self.args, priority=self.priority)
        new_task.index_chain = self.index_chain
        return new_task


def msubst(theta: Dict, tasks: Union[Task, List, Tuple]) -> Union[Task, List, Tuple]:
    """
    Perform substitutions theta on tasks across the structure (of lists and tuples).
    """
    if isinstance(tasks, Task):
        print(tasks.head, type(tasks.head))
        s = subst(theta, tasks.head)
        print(s, type(s))
        return Task(name=s[0], args=s[1:])
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


def dict_to_tuple(dict_list: List[Dict]) -> List[Tuple]:
    return [(key, d['id'], d[key]) for d in dict_list for key in d if key != 'id']


def tuples_to_dicts(tuples: Union[List, Tuple], use_facts=False, use_and_operator=False) -> List[Dict]:
    dicts = defaultdict(dict)
    for t in tuples:
        if 'id' not in dicts[t[1]]:
            dicts[t[1]]['id'] = t[1]
        dicts[t[1]][t[0]] = t[2]
    dicts = [d if not use_facts else Fact(**d) for d in dicts.values()]
    if use_and_operator:
        dicts = AND(*dicts)
    return dicts


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