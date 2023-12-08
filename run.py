from shop2.domain import Task, Operator, Method, Axiom
from shop2.planner import SHOP2

#Domain Description
Domain = {
        "axioms": [
            Axiom(head=('value-equality', '?x', '?y'), 
                  conditions=[('value', '?x', '?v'), ('value', '?y', '?v'), (lambda x, y: x<y, '?x', '?y')])
                  ],
        "assign": Operator(head=('assign', '?x', '?y'),
                        conditions=[('value', '?x', '?vx')],
                        effects=[('value', '?y', '?vx')]),

        "intAdd": Operator(head=('intAdd', '?x', '?y', '?z'),
                        conditions=[('value', '?x', '?vx'), ('value', '?y', '?vy')],
                        effects=[('value', '?z', (lambda x,y: x+y, '?vx', '?vy'))]),

        "intMult": Operator(head=('intMult', '?x', '?y', '?z'),
                        conditions=[('value', '?x', '?vx'), ('value', '?y', '?vy')],
                        effects=[('value', '?z', (lambda x,y:x*y, '?vx', '?vy'))]),

        "fracAdd": Method(head=('fracAdd', '?xn', '?yn', '?xd', '?yd'),
                          conditions=[{('value', '?xn', '?vnx'), ('value', '?yn', '?vny'), ('value', '?xd', '?vd'), ('value', '?yd', '?vd')},
                                      {('value', '?xn', '?vnx'), ('value', '?yn', '?vny'), ('value', '?xd', '?vxd'), ('value', '?yd', '?vyd')}],
                          subtasks=[[Task(head=('intAdd', 'xn', 'yn', 'nom'), primitive=True), Task(head=('assign', 'xd', 'denom'), primitive=True)],
                                    ([(Task(head=('intMult', '?xn', '?yd', 'nom1'), primitive=True), Task(head=('intMult', '?yn', '?xd', 'nom2'), primitive=True)), Task(head=('intAdd', 'nom1', 'nom2', 'nom'), primitive=True)],
                                     Task(head=('intMult', 'xd', 'yd', 'denom'), primitive=True))]),

        "fracMult": Method(head=('fracMult', '?xn', '?yn', '?xd', '?yd'),
                            conditions=[{('value', '?xn', '?vnx'), ('value', '?yn', '?vny'), ('value', '?xd', '?vxd'), ('value', '?yd', '?vyd')}],
                            subtasks=[[Task(head=('intMult', 'xn', 'yn', 'nom'), primitive=True), Task(head=('intMult', 'xd', 'yd', 'denom'), primitive=True)]]),
                            
        "add": Method(head=('add',),
                      conditions=[{('value', '?xn', '?vnx'), ('value', '?yn', '?vny'), ('value', '?xd', '?vdx'), ('value', '?yd', '?vdy'), 
                                   (lambda xn,yn,xd,yd: xn=='xn' and yn=='yn' and xd=='xd' and yd=='yd', '?xn', '?yn', '?xd', '?yd')},
                                  {('value', '?x', '?vx'), ('value', '?y', '?vy'), (lambda x,y: x!=y, '?x', '?y')}],
                      subtasks=[Task(head=('fracAdd', '?xn', '?yn', '?xd', '?yd'), primitive=False),
                                Task(head=('intAdd', '?x', '?y', 'ans'), primitive=True)]),

        "mult": Method(head=('mult',),
                          conditions=[{('value', '?xn', '?vnx'), ('value', '?yn', '?vny'), ('value', '?xd', '?vdx'), ('value', '?yd', '?vdy'),
                                       (lambda xn,yn,xd,yd: xn=='xn' and yn=='yn' and xd=='xd' and yd=='yd', '?xn', '?yn', '?xd', '?yd')},
                                      {('value', '?x', '?vx'), ('value', '?y', '?vy'), (lambda x,y: x!=y, '?x', '?y')}],
                          subtasks=[Task(head=('fracMult', '?xn', '?yn', '?xd', '?yd'), primitive=False),
                                    Task(head=('intMult', '?x', '?y', 'ans'), primitive=True)]),
                                    
        "solve":  Method(head=('solve',),
                     conditions=[{('operator', '?op', '+')}, {('operator', '?op', '*')}],
                     subtasks=[Task(head=('add',), primitive=False), Task(head=('mult',), primitive=False)])
    }

if __name__ == "__main__":

    numerator_x, numerator_y = 1, 3
    denominator_x, denominator_y = 6, 5
    operator = "*"
    state = set([('value', 'xn', numerator_x), ('value', 'yn', numerator_y), ('value', 'xd', denominator_x), ('value', 'yd', denominator_y),('operator', 'op', operator)])
    # state = set([('value', 'xn', numerator_x), ('value', 'yn', numerator_y), ('operator', 'op', operator)])

    Tasks = [Task(head=('solve',), primitive=False)]

    if result := SHOP2(state, Tasks, Domain): 
        plan, nstate = result
        print(state)
        print(sorted(nstate.difference(state)))
    else:
        print("No plan found")


    