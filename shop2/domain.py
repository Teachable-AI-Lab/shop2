from py_plan.pattern_matching import build_index, pattern_match, is_functional_term
from py_plan.unification import execute_functions, subst, unify
from typing import List, Tuple, Dict, Union
from random import choice

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
    
def msubst(theta: Dict, tasks: Union[Task, List, Tuple]) -> Union[Task, List, Tuple]:
    """
    Perform substitutions theta on tasks across the structure (of lists and tuples).
    """
    if isinstance(tasks, Task):
        return Task(subst(theta, tasks.head), tasks.primitive)
    else:
        return type(tasks)([msubst(theta, task) for task in tasks])
    
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
    def __init__(self, head, conditions=list(), subtasks=list(), cost=1):
        self.head = head
        self.name = head[0]
        self.conditions = conditions
        self.subtasks = subtasks
        self.cost = cost # TODO cost = sum of costs of operators in subtasks

    def applicable(self, task, state, plan, visited, debug=False):
        index = build_index(state)
        substitutions = unify(task.head, self.head)
        for condition, subtask in zip(self.conditions, self.subtasks):
            if (condition, state, plan) in visited:
                continue
            M = [(self.name, theta) for theta in pattern_match(condition, index, substitutions)] # Find if method's precondition is satisfied for state
            if debug:
                print("Task: {}\nCondition: {}\nState: {}\nSubstitutions: {}\nApplicable  Methods: {}\n\n".format(task.head, condition, state, substitutions, M))
            if M:
                m, theta = choice(M)
                visited.append((condition,state, plan))
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

    def applicable(self, task, state, debug=False):
        index = build_index(state)
        substitutions = unify(task.head, self.head)
        A = [(self.name, theta) for theta in pattern_match(self.conditions, index, substitutions)] # Find if operator's precondition is satisfied for state
        if debug:
                print("Task: {}\nCondition: {}\nState: {}\nSubstitutions: {}\nApplicable Operators: {}\n\n".format(task.head, self.conditions, state, substitutions, A))
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