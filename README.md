# SHOP2 Implementation in Python

## Overview

This project is an implementation of SHOP2 (Simple Hierarchical Ordered Planner 2) in Python, featuring a Horn clause inference engine. 
SHOP2 is a powerful AI planning system known for its efficiency and effectiveness in handling a variety of planning problems. Additionally, 
supports partial ordering. Our implementation leverages Python's flexibility and accessibility to provide an easy-to-use, yet powerful 
planning solution.

## Features

- **Horn Clause Inference Engine**: Utilizes a Horn clause logic system, allowing for efficient and logical problem-solving capabilities.
- **Partial Ordering**: Using tuples (unordered) and lists (ordered), the system represents partial ordering within the plan.

## Prerequisites

- Python version >= 3.8
- Install python package py_plan==1.0 

## Domain Description
### Axiom
Specify the head which will evaluate as true when the tail (conditions) are true.
```python
from shop2.domain import Axiom

equality = Axiom(head=('value-equality', '?x', '?y'), 
      conditions=[('value', '?x', '?v'), ('value', '?y', '?v'), (lambda x, y: x<y, '?x', '?y')])
```

### Operator
Consists of head, conditions, and effects. Delete effects are discerned by using the 'not' keyword in the predicate. Use lambda or normal functions for executing the operator on the bound variables. 
```python
from shop2.domain import Operator

intAdd = Operator(head=('intAdd', '?x', '?y', '?z'),
                        conditions=[('value', '?x', '?vx'), ('value', '?y', '?vy')],
                        effects=[('value', '?z', (lambda x,y: x+y, '?vx', '?vy'))]),
```

### Method
Consists of head, list of conditions for different subtasks lists, and a list of subtasks lists. A subtask can be a primitive task (Operator) or a non-primitive task (Method).
```python
from shop2.domain import Methdo

fracAdd = Method(head=('fracAdd', '?xn', '?yn', '?xd', '?yd'),
                          conditions=[[('value', '?xn', '?vnx'), ('value', '?yn', '?vny'),
                                       ('value', '?xd', '?vd'), ('value', '?yd', '?vd')], #conditions for 1st subtasks list
                                      [('value', '?xn', '?vnx'), ('value', '?yn', '?vny'),
                                       ('value', '?xd', '?vxd'), ('value', '?yd', '?vyd')]], # conditions for 2nd subtasks list
                          subtasks=[[Task(head=('intAdd', 'xn', 'yn', 'nom'), primitive=True),
                                     Task(head=('assign', 'xd', 'denom'), primitive=True)], # 1st subtasks list
                                    ([(Task(head=('intMult', '?xn', '?yd', 'nom1'), primitive=True),
                                       Task(head=('intMult', '?yn', '?xd', 'nom2'), primitive=True)),
                                       Task(head=('intAdd', 'nom1', 'nom2', 'nom'), primitive=True)],
                                       Task(head=('intMult', 'xd', 'yd', 'denom'), primitive=True))]), # 2nd subtasks list
```

### Task
Consists of a head and flag for primitive status. It can either be primitive or non-primitive. The SHOP2 planner accepts a list of tasks as input.
```python
from shop2.domain import Task

solve = Task(head=('solve',), primitive=False)
```

## Commands
```
python run.py
```
