from py_plan.pattern_matching import build_index, pattern_match, is_functional_term
from py_plan.unification import execute_functions, subst, unify
from itertools import chain
from copy import deepcopy
from random import choice
from operator import or_
from typing import List, Tuple, Set, Dict, Union


class Task:
    """
    As defined for Task in domain description of SHOP2
    """
    def __init__(self,head, primitive):
        self.head = head
        self.name = head[0]
        self.primitive = primitive
        
    def __str__(self):
        s = f"Name: {self.name}\n"
        s += f"Primitive: {self.primitive}\n"
        return s

    def __repr__(self):
        return f"<Task {self.name}>"
    
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
        for theta in pattern_match(self.conditions, index):
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
    def __init__(self, head, conditions=list(), subtasks=list(), cost=1):
        self.head = head
        self.name = head[0]
        self.conditions = conditions
        self.subtasks = subtasks
        self.cost = cost # TODO cost = sum of costs of operators in subtasks

    def applicable(self, task, state, visited):
        index = build_index(state)
        substitutions = unify(task.head, self.head)
        for condition, subtask in zip(self.conditions, self.subtasks):
            if (condition, state) in visited:
                continue
            M = [(self.name, theta) for theta in pattern_match(condition, index, substitutions)] # Find if method's precondition is satisfied for state
            if M:
                m, theta = choice(M)
                visited.append((condition,state))
                return msubst(theta, subtask)
        return False

    def __str__(self):
        s = f"Name: {self.name}\n"
        s += f"Conditions: {self.conditions}\n"
        s += f"Subtasks: {self.subtasks}\n"
        s += f"Cost: {self.cost:.2f}\n"
        return s

    def __repr__(self):
        return f"<Method {self.name}>" 
    
class Operator:
    """
    As defined for Operator in domain description of SHOP2
    """
    def __init__(self, head, conditions, effects, cost=1):
        self.head = head
        self.name = head[0]
        self.conditions = set(conditions)
        self.effects = set(effects)
        self.cost = cost

        self.add_effects = set()
        self.del_effects = set()

        for e in self.effects:
            if isinstance(e, tuple) and len(e) > 0 and e[0] == 'not':
                self.del_effects.add(e[1])
            else:
                self.add_effects.add(e)

    def applicable(self, task, state):
        index = build_index(state)
        substitutions = unify(task.head, self.head)
        A = [(self.name, theta) for theta in pattern_match(self.conditions, index, substitutions)] # Find if operator's precondition is satisfied for state

        if A:
            a, theta = choice(A)
            dels = frozenset(execute_functions(e, theta) if is_functional_term(e) else subst(theta, e) 
                             for e in self.del_effects)
            adds = frozenset(execute_functions(e, theta) if is_functional_term(e) else subst(theta, e)
                             for e in self.add_effects)
            return (dels, adds) # Return the add and delete effects of the operator
        return False
    
    def __str__(self):
        s = f"Name: {self.name}\n"
        s += f"Conditions: {self.conditions}\n"
        s += f"Effects: {self.effects}\n"
        s += f"Cost: {self.cost:.2f}\n"
        return s

    def __repr__(self):
        return f"<Operator {self.name}>" 

def msubst(theta: Dict, tasks: Union[Task, List, Tuple]) -> Union[Task, List, Tuple]:
    """
    Perform substitutions theta on tasks across the structure (of lists and tuples).
    """
    if isinstance(tasks, Task):
        return Task(subst(theta, tasks.head), tasks.primitive)
    else:
        return type(tasks)([msubst(theta, task) for task in tasks])   

def getT0(T: Union[List, Tuple]) -> Union[List, Tuple]:
    """
    Returns list/tuple of tasks which no other task in T is constrained to precede.
    """
    if isinstance(T, list) and not isinstance(T[0], (list, tuple)):
        return list([T[0]])
    elif isinstance(T, list):
        return getT0(T[0])
    elif isinstance(T, tuple):
        return tuple(chain.from_iterable(getT0(t) if isinstance(t, (list, tuple)) else (t,) for t in T))
        
def removeTask(T: Union[List, Tuple], task: Task) -> Union[List, Tuple]:
    """
    Remove task from the list or tuple T.
    """
    if isinstance(T, list):
        return [result for t in T if (result := removeTask(t, task)) != task and result]
    elif isinstance(T, tuple):
        return tuple(result for t in T if (result := removeTask(t, task)) != task and result)
    else: 
        return T

def addTask(x: Union[List, Tuple], y: Union[List, Tuple]) -> Union[List, Tuple]:
    """
    Add task(s) x to the front of the list or tuple y.
    """
    if isinstance(y, list):
        return [x] + y
    elif isinstance(y, tuple):
        return (x,) + y
         
def replaceTask(T: Union[List, Tuple, Task], task: Task, ntask: Task) -> Union[List, Tuple, Task]:
    """
    Replace task with ntask in T.
    """
    if isinstance(T, list):
        return [result for t in T if (result := replaceTask(t, task, ntask)) != ntask or result == ntask]
    elif isinstance(T, tuple):
        return tuple(result for t in T if (result := replaceTask(t, task, ntask)) != ntask or result == ntask)
    else: 
        return ntask if T.head == task.head else T

def replaceHead(tasks: Union[List, Tuple, Task]) -> Union[List, Tuple]:
    """
    Replaces the all tasks in  the structure (of lists and tuples) with just the head of the task.
    """
    if isinstance(tasks, Task):
        return tasks.head
    else:
        return type(tasks)([replaceHead(task) for task in tasks])

def execute_functions(fun, s=()):
    """
    Traverses a fact executing any functions present within. Returns a fact
    where functions are replaced with the function return value. Allows to
    return with variable unlike `py_plan.unification.execute_functions`.
    """
    if s == ():
        s = {}

    if isinstance(fun, tuple) and len(fun) > 0:
        if fun[0] == or_:
            try:
                if execute_functions(fun[1], s) is not False:
                    return True
            except TypeError as e:
                if execute_functions(fun[2], s) is not False:
                    return True
                raise e
            return execute_functions(fun[2], s)

        if callable(fun[0]):
            return fun[0](*[execute_functions(ele, s) for ele in fun[1:]])
        else:
            return tuple(execute_functions(ele, s) for ele in fun)
    if fun in s:
        return execute_functions(s[fun])

    return fun

def SHOP2(state: Set, T: Union[List, Tuple], D: Dict) -> Union[List, Tuple, bool]:
    """
    Implementation of the SHOP2 algorithm. Returns a plan and 
    the final state if viable plan is possible, otherwise returns 
    False.
    """
    plan = deepcopy(T)
    stack, visited = list(), list() # used for backtracking from invalid plan
    while True:
        if not T:
            return replaceHead(plan), state 
        for axiom in D.get('axioms', []):
            state = axiom.applicable(state)
        T0 = getT0(T)
        task = choice(T0) # non-deterministic choice
        if task.primitive:
            if (result := D[task.name].applicable(task, state)):
                dels, adds = result
                state = state.difference(dels).union(adds)
                T = removeTask(T, task)
            else:
                if stack: # backtrack
                    T, plan, state = stack.pop()
                else:
                    return False
        else:
            if (result := D[task.name].applicable(task, state, visited)):
                stack.append((deepcopy(T), deepcopy(plan), deepcopy(state)))
                subtask = result
                plan = replaceTask(plan, task, subtask)
                T = type(T)([subtask])+removeTask(T, task)
            else:
                if stack: # backtrack
                    T, plan, state = stack.pop()
                else:
                    return False
