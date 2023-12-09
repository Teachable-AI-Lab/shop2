# Python SHOP2

![Build Status](https://github.com/Teachable-AI-Lab-TAIL/shop2/workflows/Build/badge.svg)

## Overview

This project is a Python implementation of SHOP2 (Simple Hierarchical Ordered Planner 2), featuring a Horn clause inference engine. 
SHOP2 is a powerful AI planning system known for its efficiency and effectiveness in handling a variety of planning problems. Additionally,
in this implementation, the plan can express partial ordering. Refer to [Nau et al. 2003](https://www.cs.umd.edu/~nau/papers/nau2003shop2.pdf)
for more details.

## Features

- **Horn Clause Inference Engine**: Utilizes a Horn clause logic system, allowing for efficient and logical problem-solving capabilities.
- **Partial Ordering**: Using tuples (unordered) and lists (ordered), the system represents partial ordering within the plan.

## Prerequisites

- Python version >= 3.8

## Installation 
```
git clone https://github.com/Teachable-AI-Lab-TAIL/shop2.git

pip install git+https://github.com/Teachable-AI-Lab-TAIL/shop2.git
```

## Domain Description
### Axiom
Specify the head which will evaluate as true when the tail (conditions) are true. The code snippet shows an axiom that returns a tuple when two values are equal in the state.
```python
from shop2.domain import Axiom

equality = Axiom(head=('value-equality', '?x', '?y'), 
                 conditions=[('value', '?x', '?v'), ('value', '?y', '?v'),
                             (lambda x, y: x<y, '?x', '?y')])
```

### Operator
Consists of head, conditions, and effects. Delete effects are discerned by using the 'not' keyword in the predicate. Use lambda or normal functions for executing the operator on the bound variables. The code snippet shows the operator for adding two numbers.
```python
from shop2.domain import Operator

intAdd = Operator(head=('intAdd', '?x', '?y', '?z'),
                  conditions=[('value', '?x', '?vx'), ('value', '?y', '?vy')],
                  effects=[('value', '?z', (lambda x,y: x+y, '?vx', '?vy'))]),
```

### Method
Consists of a head, a list of conditions for different subtasks lists, and a list of subtasks lists. A subtask can be a primitive task (Operator) or a non-primitive task (Method). The code snippet shows the high-level method for fraction addition, which decomposes based on the nature of the denominator. If denominators are equal, you add the numerators and return the denominator. While, if denominators are different, the formula includes multiplying the other number's denominator with their numerator before adding and dividing by the product of the two denominators.

```python
from shop2.domain import Method

fracAdd = Method(head=('fracAdd', '?xn', '?yn', '?xd', '?yd'),
                 conditions=[[('value', '?xn', '?vnx'), ('value', '?yn', '?vny'),
                              ('value', '?xd', '?vd'), ('value', '?yd', '?vd')], # 1st subtasks list conds
                             [('value', '?xn', '?vnx'), ('value', '?yn', '?vny'),
                              ('value', '?xd', '?vxd'), ('value', '?yd', '?vyd')]], # 2nd subtasks list conds
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

For further details refer to run.py.

## Planner
The planner SHOP2 requires state, tasks, and the domain description as arguments. There is an optional debug argument, which provides verbose details of the planner, enabling robust debugging.

```python
from shop2.planner import SHOP2

state = set([('value', 'xn', 4), ('value', 'yn', 1), ('operator', 'op', '+')])
Domain = {...}
Tasks = [Task(head=('solve',), primitive=False)]

plan, state = SHOP2(state, Tasks, Domain)
```
## Commands
```
python run.py
```

## Contact Information

For support, questions, or contributions, please contact us:

- **Email**: [msiddiqui66@gatech.edu](mailto:msiddiqui66@gatech.edu)
- **GitHub Issues**: [Submit Issue](https://github.com/Teachable-AI-Lab-TAIL/shop2/issues)
