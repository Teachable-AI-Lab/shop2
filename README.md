# Python SHOP2 with Facts

![Build Status](https://github.com/Teachable-AI-Lab-TAIL/shop2/workflows/Build/badge.svg)

## Overview

This project is a Python implementation of SHOP2 (Simple Hierarchical Ordered Planner 2) with Facts from Py_RETE instead of predicate tuples.
SHOP2 is a powerful AI planning system known for its efficiency and effectiveness in handling a variety of planning problems and Facts provide simplicity in authoring domains. Additionally, in this implementation, the plan can express partial ordering along. Refer to [Nau et al. 2003](https://www.cs.umd.edu/~nau/papers/nau2003shop2.pdf) and [py_rete](https://github.com/cmaclell/py_rete/tree/master)
for more details.

## Features
- **Facts**: Supports Facts along with logical operators like AND, OR and NOT
- **Horn Clause Inference Engine**: Utilizes a Horn clause logic system, allowing for efficient and logical problem-solving capabilities.
- **Partial Ordering**: Using tuples (unordered) and lists (ordered), the system represents partial ordering within the plan.

## Prerequisites

- Python version >= 3.8

## Installation 
```
git clone https://github.com/Teachable-AI-Lab-TAIL/shop2.git

pip install git+https://github.com/Teachable-AI-Lab-TAIL/shop2.git@facts
```

## Domain Description
### Operator
Consists of head, precondition, and effects. Delete effects are discerned by using the 'not' keyword in the predicate. Use lambda or normal functions for executing the operator on the bound variables. The code snippet shows the operator for adding two numbers.
```python
from shop2.domain import Operator

intAdd = Operator(head=('intAdd', V('x'), V('y'), V('z')),
                        precondition=(Fact(field=V('x'), value=V('vx'))&Fact(field=V('y'), value=V('vy'))),
                        effects=[Fact(field=V('z'), value=(lambda x,y: x+y, V('vx'), V('vy')))]),
```

### Method
Consists of a head, a list of preconditions for different subtasks lists, and a list of subtasks lists. A subtask can be a primitive task (Operator) or a non-primitive task (Method). The code snippet shows the high-level method for fraction addition, which decomposes based on the nature of the denominator. If denominators are equal, you add the numerators and return the denominator. While, if denominators are different, the formula includes multiplying the other number's denominator with their numerator before adding and dividing by the product of the two denominators.

```python
from shop2.domain import Method

"fracAdd": Method(head=('fracAdd', V('xn'), V('yn'), V('xd'), V('yd')),
                          preconditions=[(Fact(field=V('xn'),value=V('vnx'))&Fact(field=V('yn'),value=V('vny'))&Fact(field=V('xd'),value=V('vd'))&Fact(field=V('yd',value=V('vd'))),
                                      (Fact(field=V('xn'),value=V('vnx'))&Fact(field=V('yn'),value=V('vny'))&Fact(field=V('xd'),value=V('vxd'))&Fact(field=V('yd',value=V('vyd')))],
                          subtasks=[[Task(head=('intAdd', 'xn', 'yn', 'nom'), primitive=True), Task(head=('assign', 'xd', 'denom'), primitive=True)],
                                    ([(Task(head=('intMult', V('xn'), V('yd'), 'nom1'), primitive=True), Task(head=('intMult', V('yn'), V('xd'), 'nom2'), primitive=True)), Task(head=('intAdd', 'nom1', 'nom2', 'nom'), primitive=True)],
                                     Task(head=('intMult', 'xd', 'yd', 'denom'), primitive=True))]),
```

### Task
Consists of a head and flag for primitive status. It can either be primitive or non-primitive. The SHOP2 planner accepts a list of tasks as input.
```python
from shop2.domain import Task

solve = Task(head=('solve',), primitive=False)
```

For further details refer to run.py.

## Planner

### SHOP2
The planner SHOP2 requires state, tasks, and the domain description as arguments. There is an optional debug argument, which provides verbose details of the planner, enabling robust debugging.

```python
from shop2.planner import SHOP2

state = Fact(field='num_x', value=10)&Fact(field='den_x',value=12)
Tasks = [Task(head=('fracAdd',), primitive=False)]
Domain = {...}
plan = SHOP2(state=state, T=Tasks, D=Domain)
```
### Coroutine Planner
The coroutine planner waits for you to send some data to the generator. In order for the generator to terminate, it has to yield the final Fact. Checkout examples/fraction_tutor.py for more details.
```python
state = Fact(field='num_x', value=10)&Fact(field='den_x',value=12)
Tasks = [Task(head=('fracAdd',), primitive=False)]
final = Fact(value="done")
plan = CoroutinePlanner(state=state, T=Tasks, D=Domain, final=final)
received = plan.send(None)
```
## Integration with py_rete Facts
It supports AND, OR and NOT operator along with maintaining De Morgan's law.


```python
from shop2.fact import Fact
state = Fact(value=1) & Fact(value=2)
>>> AND(Fact(value=1), Fact(value=2))
state = ~state
>>> OR(NOT(Fact(value=1),), NOT(Fact(value=2),))
```
## Commands
```
python run.py
```

## Contact Information

For support, questions, or contributions, please contact us:

- **Email**: [msiddiqui66@gatech.edu](mailto:msiddiqui66@gatech.edu)
- **GitHub Issues**: [Submit Issue](https://github.com/Teachable-AI-Lab-TAIL/shop2/issues)
