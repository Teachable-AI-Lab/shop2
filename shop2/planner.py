from copy import deepcopy
from random import choice
from typing import List, Tuple, Set, Dict, Union
from shop2.domain import Task, Axiom, Method 
from shop2.utils import replaceHead, replaceTask, removeTask, getT0

def SHOP2(state: Set, T: Union[List, Tuple], D: Dict, debug=False) -> Union[List, Tuple, bool]:
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
            if (result := D[task.name].applicable(task, state, debug=debug)):
                dels, adds = result
                state = state.difference(dels).union(adds)
                T = removeTask(T, task)
            else:
                if stack: # backtrack
                    if debug:
                        print("Backtracking...")
                    T, plan, state = stack.pop()
                else:
                    return False
        else:
            if (result := D[task.name].applicable(task, state, str(plan), visited, debug=debug)): # NOTE plan is passed as string just because it is more convenient to pass it as string than its original structure
                stack.append((deepcopy(T), deepcopy(plan), deepcopy(state)))
                subtask = result
                plan = replaceTask(plan, task, subtask)
                T = type(T)([subtask])+removeTask(T, task)
            else:
                if stack: # backtrack
                    if debug:
                        print("Backtracking...")
                    T, plan, state = stack.pop()
                else:
                    return False