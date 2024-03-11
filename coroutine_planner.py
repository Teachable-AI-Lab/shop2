# app.py
from random import randint
from shop2.domain import Task, Method, Operator, Axiom
from py_rete.fact import Fact
from py_rete.common import V
from py_rete.conditions import Filter, NOT
import math

from copy import deepcopy
from random import choice
from typing import List, Tuple, Set, Dict, Union, Generator
from shop2.domain import Task, Axiom, Method, flatten
from shop2.utils import replaceHead, replaceTask, removeTask, getT0, generatePermute
from shop2.fact import Fact
from shop2.conditions import AND

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
            result = D[task.name].applicable(task, state, str("plan"), visited, debug)
            print(state)
            print(D[task.name].conditions)
            print(result)
            if result:
                subtask = result
                T = type(T)([subtask])+removeTask(T, task)
                # T = flatten_structure(T) NOTE: Commented for now as I don't think its needed but do add again if a usecase arises
                permutations = generatePermute(T)
                for t in reversed(permutations):
                    stack.append((t, deepcopy(state)))
            else:
                yield from backtrack()

Domain = {
    "intAdd": Operator(head=('intAdd', V('x'), V('y'), V('z')),
                        conditions=(Fact(field=V('x'), value=V('vx'))&Fact(field=V('y'), value=V('vy'))),
                        effects=[Fact(field=V('z'), value=(lambda x,y: x+y, V('vx'), V('vy')))]),

    "intMult": Operator(head=('intMult', V('x'), V('y'), V('z')),
                        conditions=(Fact(field=V('x'), value=V('vx'))&Fact(field=V('y'), value=V('vy'))),
                        effects=[Fact(field=V('z'), value=(lambda x,y: x*y, V('vx'), V('vy')))]),

    "find_num_with_lcm": Operator(head=('find_num_with_lcm', V('xn'), V('x') , V('y'), V('z')),
                                  conditions=(Fact(field=V('x'), value=V('xv'))&Fact(field=V('y'), value=V('vy'))&Fact(field=V('xn'), value=V('xnv'))),
                                  effects=[Fact(field=V('z'), value=(lambda xn,x,y: int(xn*((abs(x*y)//math.gcd(x,y))/x)), V('xnv'), V('xv'), V('vy')))]),

    "find_den_with_lcm": Operator(head=('find_den_with_lcm', '?x' , '?y', '?z'),
                                  conditions=(Fact(field=V('x'), value=V('vx'))&Fact(field=V('y'), value=V('vy'))),
                                  effects=[Fact(field=V('z'), value=(lambda x,y: int(abs(x*y)//math.gcd(x,y)), V('vx'), V('vy')))]),

    "fracAdd": Method(head=('fracAdd',),
                      conditions=[~Fact(field="button", value="done"), ~Fact(field="button", value="done")],
                      subtasks=[[Task(head=('cross_Mult',), primitive=False)], 
                                [Task(head=('lcm',), primitive=False)]]
                    ),

    "cross_Mult": Method(head=('cross_Mult',),
                        conditions=[~Fact(field="button", value="done")],
                        subtasks=[(Task(head=('get_num_cross_Mult',) ,primitive=False), 
                                   Task(head=('get_den_cross_Mult',), primitive=False))]
                        ),

    "lcm": Method(head=('lcm',),
                  conditions=[~Fact(field="button", value="done")],
                  subtasks=[(Task(head=('get_num_lcm',), primitive=False), 
                             Task(head=('get_den_lcm',), primitive=False))]
                  ),

    "get_num_cross_Mult": Method(head=('get_num_cross_Mult',),
                                conditions=[~Fact(field="button", value="done")],
                                subtasks=[[(Task(head=('intMult', 'num_x', 'den_y', 'n1xd2'), primitive=True), 
                                            Task(head=('intMult', 'num_y', 'den_x', 'n2xd1'), primitive=True)),
                                            Task(head=('intAdd', 'n1xd2', 'n2xd1', 'num'), primitive=True)]]
                                ),

    "get_den_cross_Mult": Method(head=('get_den_cross_Mult',),
                                 conditions=[~Fact(field="button", value="done")],
                                 subtasks=[[Task(head=('intMult', 'den_x', 'den_y', 'denom'), primitive=True)]]
                                 ),

    "get_num_lcm": Method(head=('get_num_lcm',),
                          conditions=[~Fact(field="button", value="done")],
                          subtasks=[[(Task(head=('find_num_with_lcm', 'num_x', 'den_x', 'den_y', 'n1xd2'), primitive=True), 
                                      Task(head=('find_num_with_lcm', 'num_y', 'den_y', 'den_x', 'n2xd1'), primitive=True)), 
                                      Task(head=('intAdd', 'n1xd2', 'n2xd1', 'num'), primitive=True)]]
                        ),

    "get_den_lcm": Method(head=('get_den_lcm',),
                          conditions=[~Fact(field="button", value="done")],
                          subtasks=[[Task(head=('find_den_with_lcm', 'den_x', 'den_y', 'denom'), primitive=True)]]
                          ),
    
}

if __name__ == "__main__":

    den_x = randint(2,9)
    num_x = randint(1,den_x-1)
    den_y = randint(2,9)
    while den_y == den_x:
        den_y = randint(2,9)
    num_y = randint(1,den_y-1)
    den_x, num_x, den_y, num_y = 6,5,4,2
    state = Fact(field='num_x', value=num_x)&Fact(field='den_x', value=den_x)&Fact(field='num_y', value=num_y)&Fact(field='den_y', value=den_y)
    Tasks = [Task(head=('fracAdd',), primitive=False)]
    ending_fact = Fact(value="done")
    plan = CoroutinePlanner(state=state, T=Tasks, D=Domain, final=ending_fact)
    expected = plan.send(None)
    print(f"{num_x}/{den_x} + {num_y}/{den_y} = ?")
    print(expected)
    while expected != ending_fact:
        field = input("Which field would you like to fill?\n1.n1xd2\n2.n2xd1\n3.denom\n4.num\n")
        value = int(input(f"What value would you like to fill in {field}?\n"))
        answer = Fact(field=field, value=value)
        while answer != expected:
            expected = plan.send(False)
            print(expected)
        expected = plan.send(True)
    # print("PROBLEM SOLVED")