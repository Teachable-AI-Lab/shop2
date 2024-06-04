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
    def __init__(self, head, preconditions, subtasks, cost=1):
        self.head = head
        self.name = head[0]
        self.args = head[1:]
        self.preconditions = preconditions
        self.subtasks = subtasks
        self.cost = cost # TODO cost = sum of costs of operators in subtasks

    def applicable(self, task, state, plan, visited):
        ptstate = fact2tuple(state, variables=False)[0]
        index = build_index(ptstate)
        substitutions = unify(task.head, self.head)
        if not self.preconditions:
            return msubst(substitutions, self.subtasks)
        ptconditions = fact2tuple(self.preconditions, variables=True)
        for ptcondition in ptconditions:
            if (task.name, str(ptcondition), str(state), plan) in visited:
                continue
            visited.append((task.name, str(ptcondition),str(state), plan))
            M = [(self.name, theta) for theta in pattern_match(ptcondition, index, substitutions)] # Find if method's precondition is satisfied for state
            if M:
                m, theta = choice(M)
                return msubst(theta, self.subtasks)

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
    def __init__(self, head, preconditions, effects, cost=1):
        self.head = head
        self.name = head[0]
        self.args = head[1:]
        self.preconditions = preconditions
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
        add_effects, del_effects = set(), set()
        for effect in self.add_effects:
            add_effects.add(effect.duplicate())
        for effect in self.del_effects:
            del_effects.add(effect.duplicate())

        ptstate = fact2tuple(state, variables=False)[0]
        index = build_index(ptstate)        
        substitutions = unify(task.head, self.head)
        if not self.preconditions:
            grounded_args = tuple([substitutions[f'?{v.name}'] for v in self.args if f'?{v.name}' in substitutions])
            return  (self.name, grounded_args)
        ptconditions = fact2tuple(self.preconditions, variables=True)
        for ptcondition in ptconditions:
            A = [(self.name, theta) for theta in pattern_match(ptcondition, index, substitutions)]
            if A:
                a, theta = choice(A)
                grounded_args = tuple([theta[f'?{v.name}'] for v in self.args if f'?{v.name}' in theta]) 
                return (self.name, grounded_args)
        return False
    
    def __str__(self):
        s = f"Name: {self.name}\n"
        s += f"Preconditions: {self.preconditions}\n"
        s += f"Effects: {self.effects}\n"
        return s

    def __repr__(self):
        return f"<Operator {self.name}>" 


@dataclass(eq=True, frozen=True)
class Task:
    name: str
    args: Tuple[Union[str, 'V'], ...]

    def __init__(self, name: str, *args: Union[str, 'V']):
        object.__setattr__(self, 'name', name)
        object.__setattr__(self, 'args', args)

    @property
    def head(self):
        return (self.name, *self.args)


