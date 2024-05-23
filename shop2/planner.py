from copy import deepcopy
from random import choice
from typing import List, Tuple, Set, Dict, Union, Generator
from shop2.domain import Task, Axiom, Method, flatten, Operator
from shop2.utils import replaceHead, replaceTask, removeTask, getT0, generatePermute
from shop2.fact import Fact
from shop2.conditions import AND


def planner(state: Fact, T: Union[List, Tuple], D: Dict):
    plan = []
    stack, inner_visited, outer_visited = [], [], []
    while True:
        if not T:
            raise StopException(plan)
        T0 = getT0(T)
        task = choice(T0) 
        success = False
        key = f"{ task.name }/{ len(task.args) }"
        for action in D[key]:
            print(key, action.preconditions)
            if isinstance(action, Operator):
                if (result := action.applicable(task, state)):
                    print("RESULT", result)
                    success, state = yield result
                    if success:
                        T = removeTask(T, task)
                        plan.append(action)
                    break

            elif isinstance(action, Method):
                if (result := action.applicable(task, state, str(plan), inner_visited)):
                    print("RESULT", result)
                    stack.append((deepcopy(T), deepcopy(plan), deepcopy(state)))
                    subtask = result
                    T = type(T)([subtask])+removeTask(T, task)
                    success = True
                    break
            
            if (str(action.head), str(action.preconditions), str(state)) in outer_visited:
                break
            else:
                outer_visited.append((str(action.head), str(action.preconditions), str(state)))

        if not success:
            if stack: 
                T, plan, state = stack.pop()
                state = AND(*flatten(state))
            else:
                raise FailedPlanException(message="No valid plan found")
                

class StopException(Exception):
    """Exception raised for errors in the execution of a plan.

    Attributes:
        plan -- the plan that caused the error
        message -- explanation of the error
    """

    def __init__(self, plan=None, message="Task Completed"):
        self.plan = plan
        self.message = message
        super().__init__(self.message)

    def __str__(self):
        return f'{self.plan} -> {self.message}'
    
class FailedPlanException(Exception):
    """Exception raised for errors in the execution of a plan.

    Attributes:
        plan -- the plan that caused the error
        message -- explanation of the error
    """

    def __init__(self, plan=None, message="The plan execution failed"):
        self.plan = plan
        self.message = message
        super().__init__(self.message)

    def __str__(self):
        return f'{self.plan} -> {self.message}'