# app.py
import math
from random import randint
from shop2.domain import Task, Method, Operator
from shop2.fact import Fact
from shop2.common import V
from shop2.fact import Fact
from shop2.planner import CoroutinePlanner

Domain = {
    "intAdd": Operator(head=('intAdd', V('x'), V('y'), V('z')),
                        precondition=(Fact(field=V('x'), value=V('vx'))&
                                      Fact(field=V('y'), value=V('vy'))),
                        effects=Fact(field=V('z'), value=(lambda x,y: x+y, V('vx'), V('vy')))),

    "intMult": Operator(head=('intMult', V('x'), V('y'), V('z')),
                        precondition=(Fact(field=V('x'), value=V('vx'))&
                                      Fact(field=V('y'), value=V('vy'))),
                        effects=Fact(field=V('z'), value=(lambda x,y: x*y, V('vx'), V('vy')))),

    "find_num_with_lcm": Operator(head=('find_num_with_lcm', V('xn'), V('x') , V('y'), V('z')),
                                  precondition=(Fact(field=V('x'), value=V('xv'))&
                                                Fact(field=V('y'), value=V('vy'))&
                                                Fact(field=V('xn'), value=V('xnv'))),
                                  effects=Fact(field=V('z'), value=(lambda xn,x,y: int(xn*((abs(x*y)//math.gcd(x,y))/x)), V('xnv'), V('xv'), V('vy')))),

    "find_den_with_lcm": Operator(head=('find_den_with_lcm', '?x' , '?y', '?z'),
                                  precondition=(Fact(field=V('x'), value=V('vx'))&
                                                Fact(field=V('y'), value=V('vy'))),
                                  effects=Fact(field=V('z'), value=(lambda x,y: int(abs(x*y)//math.gcd(x,y)), V('vx'), V('vy')))),

    "fracAdd": Method(head=('fracAdd',),
                      preconditions=[~Fact(field="button", value="done"), 
                                     ~Fact(field="button", value="done")],
                      subtasks=[[Task(head=('cross_Mult',), primitive=False)], 
                                [Task(head=('lcm',), primitive=False)]]
                    ),

    "cross_Mult": Method(head=('cross_Mult',),
                        preconditions=[~Fact(field="button", value="done")],
                        subtasks=[(Task(head=('get_num_cross_Mult',) ,primitive=False), 
                                   Task(head=('get_den_cross_Mult',), primitive=False))]
                        ),

    "lcm": Method(head=('lcm',),
                  preconditions=[~Fact(field="button", value="done")],
                  subtasks=[(Task(head=('get_num_lcm',), primitive=False), 
                             Task(head=('get_den_lcm',), primitive=False))]
                  ),

    "get_num_cross_Mult": Method(head=('get_num_cross_Mult',),
                                preconditions=[~Fact(field="button", value="done")],
                                subtasks=[[(Task(head=('intMult', 'num_x', 'den_y', 'n1xd2'), primitive=True), 
                                            Task(head=('intMult', 'num_y', 'den_x', 'n2xd1'), primitive=True)),
                                            Task(head=('intAdd', 'n1xd2', 'n2xd1', 'num'), primitive=True)]]
                                ),

    "get_den_cross_Mult": Method(head=('get_den_cross_Mult',),
                                 preconditions=[~Fact(field="button", value="done")],
                                 subtasks=[[Task(head=('intMult', 'den_x', 'den_y', 'denom'), primitive=True)]]
                                 ),

    "get_num_lcm": Method(head=('get_num_lcm',),
                          preconditions=[~Fact(field="button", value="done")],
                          subtasks=[[(Task(head=('find_num_with_lcm', 'num_x', 'den_x', 'den_y', 'n1xd2'), primitive=True), 
                                      Task(head=('find_num_with_lcm', 'num_y', 'den_y', 'den_x', 'n2xd1'), primitive=True)), 
                                      Task(head=('intAdd', 'n1xd2', 'n2xd1', 'num'), primitive=True)]]
                        ),

    "get_den_lcm": Method(head=('get_den_lcm',),
                          preconditions=[~Fact(field="button", value="done")],
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
    state = Fact(field='num_x', value=num_x)&Fact(field='den_x', value=den_x)&Fact(field='num_y', value=num_y)&Fact(field='den_y', value=den_y)
    Tasks = [Task(head=('fracAdd',), primitive=False)]
    ending_fact = Fact(value="done")
    plan = CoroutinePlanner(state=state, T=Tasks, D=Domain, final=ending_fact)
    expected = plan.send(None)
    print(f"{num_x}/{den_x} + {num_y}/{den_y} = ____")
    ask = "Which field would you like to fill?\nn1xd2\tn2xd1\tdenom\tnum\t\n"
    while expected != ending_fact:
        field = input(ask)
        value = int(input(f"What value would you like to fill in {field}?\n"))
        answer = Fact(field=field, value=value)
        while answer != expected:
            expected = plan.send(False) # NOTE: Sending False to indicate not a match
            if not isinstance(expected, Fact):
                print("That was incorrect")
                print(f"{num_x}/{den_x} + {num_y}/{den_y} = ?")
                field = input(ask)
                value = int(input(f"What value would you like to fill in {field}?\n"))
                answer = Fact(field=field, value=value)
            
        print("That was correct!")
        print(f"{num_x}/{den_x} + {num_y}/{den_y} = ____")
        ask = ask.replace(f"{field}\t", "")
        
        expected = plan.send(True) # NOTE: Sending True to indicate a match