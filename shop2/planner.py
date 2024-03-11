from copy import deepcopy
from random import choice
from typing import List, Tuple, Set, Dict, Union, Generator
from shop2.domain import Task, Axiom, Method, flatten
from shop2.utils import replaceHead, replaceTask, removeTask, getT0, generatePermute
from shop2.fact import Fact
from shop2.conditions import AND

def SHOP2(state: Fact, T: Union[List, Tuple], D: Dict, debug=False) -> Union[List, Tuple, bool]:
    """
    Implementation of the SHOP2 algorithm. Returns a plan and 
    the final state if viable plan is possible, otherwise returns 
    False.
    """
    plan = deepcopy(T)
    stack, visited = list(), list() # used for backtracking from invalid plan
    while True:
        if not T:
            return plan, state 

        T0 = getT0(T)
        task = choice(T0) # non-deterministic choice
        if task.primitive:
            if (result := D[task.name].applicable(task, state, debug=debug)):
                del_effects, add_effects = result
                for effect in del_effects:
                    state = state & ~effect
                for effect in add_effects:
                    state = state & effect
                T = removeTask(T, task)
            else:
                if stack: # backtrack
                    if debug:
                        print("Backtracking...")
                    T, plan, state = stack.pop()
                    state = AND(*flatten(state))
                else:
                    return False
        else:
            if (result := D[task.name].applicable(task, state, str(plan), visited, debug=debug)):
                stack.append((deepcopy(T), deepcopy(plan), deepcopy(state)))
                subtask = result
                plan = replaceTask(plan, task, subtask)
                T = type(T)([subtask])+removeTask(T, task)
            else:
                if stack: # backtrack
                    if debug:
                        print("Backtracking...")
                    T, plan, state = stack.pop()
                    state = AND(*flatten(state))
                else:
                    return False
                


def CoroutinePlanner(state:Fact, T: Union[List, Tuple], D: Dict, final: Fact, debug: bool = False) -> Generator:

    def backtrack():
        nonlocal T, state, stack, visited, correctpath
        if stack:
            T, state = stack.pop()
            state = AND(*flatten(state))
        else:
            stack, visited = correctpath.pop()
            if not correctpath:
                correctpath.append((deepcopy(stack), deepcopy(visited)))
            T, state = stack.pop()
            state = AND(*flatten(state))
            stack.append((deepcopy(T), deepcopy(state)))
            yield False

    stack, visited, correctpath = list(), list(), list()
    stack.append((deepcopy(T), deepcopy(state)))
    correctpath.append((deepcopy(stack), deepcopy(visited)))

    while True:
        if not T:
            yield final

        T0 = getT0(T)
        task = T0[0]

        if task.primitive:
            result = D[task.name].applicable(task, state, debug)
            if result:
                del_effects, add_effects = result
                for effect in del_effects:
                    state = state & ~effect
                for effect in add_effects:
                    state = state & effect

                T = removeTask(T, task)

                correct = yield list(add_effects).pop()
                if correct:
                    stack = [(deepcopy(T), deepcopy(state))]
                    correctpath = [(deepcopy(stack), deepcopy(visited))]
                else:
                    yield from backtrack()
            else:
                yield from backtrack()
        else:
            result = D[task.name].applicable(task, state, str(), visited, debug)
            
            if result:
                subtask = result
                T = type(T)([subtask])+removeTask(T, task)
                # T = flatten_structure(T) NOTE: Commented for now as I don't think its needed but do add again if a usecase arises
                permutations = generatePermute(T)
                for t in reversed(permutations):
                    stack.append((t, deepcopy(state)))
            else:
                yield from backtrack()