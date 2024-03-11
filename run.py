from shop2.domain import Task, Operator, Method
from shop2.planner import SHOP2
from shop2.fact import Fact
from shop2.common import V
from shop2.conditions import Filter, NOT


#Domain Description
Domain = {
        "intAdd": Operator(head=('intAdd', V('x'), V('y'), V('z')),
                        precondition=(Fact(field=V('x'), value=V('vx'))&
                                      Fact(field=V('y'), value=V('vy'))),
                        effects=Fact(field=V('z'), value=(lambda x,y: x+y, V('vx'), V('vy')))),

        "intMult": Operator(head=('intMult', V('x'), V('y'), V('z')),
                        precondition=(Fact(field=V('x'), value=V('vx'))&
                                      Fact(field=V('y'), value=V('vy'))),
                        effects=Fact(field=V('z'), value=(lambda x,y: x*y, V('vx'), V('vy')))),

        "fracAdd": Method(head=('fracAdd', V('xn'), V('yn'), V('xd'), V('yd')),
                          preconditions=[(Fact(field=V('xn'), value=V('vnx'))& 
                                          Fact(field=V('yn'), value=V('vny'))& 
                                          Fact(field=V('xd'), value=V('vd'))& 
                                          Fact(field=V('yd'), value=V('vd'))),
                                         (Fact(field=V('xn'), value=V('vnx'))& 
                                          Fact(field=V('yn'), value=V('vny'))& 
                                          Fact(field=V('xd'), value=V('vxd'))& 
                                          Fact(field=V('yd'), value=V('vyd')))],
                          subtasks=[[Task(head=('intAdd', 'xn', 'yn', 'nom'), primitive=True), Task(head=('assign', 'xd', 'denom'), primitive=True)],
                                    ([(Task(head=('intMult', V('xn'), V('yd'), 'nom1'), primitive=True), Task(head=('intMult', V('yn'), V('xd'), 'nom2'), primitive=True)), Task(head=('intAdd', 'nom1', 'nom2', 'nom'), primitive=True)],
                                     Task(head=('intMult', 'xd', 'yd', 'denom'), primitive=True))]),

        "fracMult": Method(head=('fracMult', V('xn'), V('yn'), V('xd'), V('yd')),
                            preconditions=[(Fact(field=V('xn'), value=V('vnx'))&
                                            Fact(field=V('yn'), value=V('vny'))&
                                            Fact(field=V('xd'), value=V('vxd'))&
                                            Fact(field=V('yd'), value=V('vyd')))],
                            subtasks=[[Task(head=('intMult', 'xn', 'yn', 'nom'), primitive=True), Task(head=('intMult', 'xd', 'yd', 'denom'), primitive=True)]]),
                            
        "add": Method(head=('add',),
                      preconditions=[(Fact(field=V('xn'), value=V('vnx'))&
                                      Fact(field=V('yn'), value=V('vny'))&
                                      Fact(field=V('xd'), value=V('vdx'))&
                                      Fact(field=V('yd'), value=V('vdy'))&
                                      Filter(lambda xn,yn,xd,yd: xn=='xn' and yn=='yn' and xd=='xd' and yd=='yd')),
                                     (Fact(field=V('x'), value=V('vx'))&Fact(field=V('y'), value=V('vy'))&Filter(lambda x,y: x!=y))],
                      subtasks=[Task(head=('fracAdd', V('xn'), V('yn'), V('xd'), V('yd')), primitive=False),
                                Task(head=('intAdd', V('x'), V('y'), 'ans'), primitive=True)]),

        "mult": Method(head=('mult',),
                          preconditions=[(Fact(field=V('xn'), value=V('vnx'))&
                                          Fact(field=V('yn'), value=V('vny'))&
                                          Fact(field=V('xd'), value=V('vdx'))&
                                          Fact(field=V('yd'), value=V('vdy'))&
                                          Filter(lambda xn,yn,xd,yd: xn=='xn' and yn=='yn' and xd=='xd' and yd=='yd')),
                                         (Fact(field=V('x'), value=V('vx'))&
                                          Fact(field=V('y'), value=V('vy'))&
                                          Filter(lambda x,y: x!=y))],
                          subtasks=[Task(head=('fracMult', V('xn'), V('yn'), V('xd'), V('yd')), primitive=False),
                                    Task(head=('intMult', V('x'), V('y'), 'ans'), primitive=True)]),
                                    
        "solve":  Method(head=('solve',),
                     preconditions=[Fact(field=V('op'), operator='+'), Fact(field=V('op'), operator='*')],
                     subtasks=[Task(head=('add',), primitive=False), Task(head=('mult',), primitive=False)])
}

if __name__ == "__main__":

    numerator_x, numerator_y = 1, 3
    denominator_x, denominator_y = 6, 5
    operator = "+"
    state = (Fact(field='op', operator=operator)&
             Fact(field='xn', value=numerator_x)&
             Fact(field='yn', value=numerator_y)&
             Fact(field='xd', value=denominator_x)&
             Fact(field='yd', value=denominator_y))

    Tasks = [Task(head=('solve',), primitive=False)]

    if result := SHOP2(state, Tasks, Domain, debug=False): 
        plan, nstate = result
        print(state)
        print(nstate)
    else:
        print("No plan found")


    