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

pip install git+https://github.com/Teachable-AI-Lab-TAIL/shop2.git
```

## Domain Description
### Operator
Consists of head, precondition, and effects. Delete effects are discerned by using the 'not' keyword in the predicate. Use lambda or normal functions for executing the operator on the bound variables. The code snippet shows the operator for multiply two numbers.
```python
from shop2.domain import Operator

intMult = Operator(head=('intMult', V('x'), V('y'), V('z')),
                preconditions=(Fact(field=V('x'), value=V('vx'))&
                            Fact(field=V('y'), value=V('vy'))),
                effects=Fact(field=V('z'), value=(lambda x,y: x*y, V('vx'), V('vy')))),
```

### Method
Consists of a head, a list of preconditions for different subtasks lists, and a list of subtasks lists. A subtask can be a primitive task (Operator) or a non-primitive task (Method). The code snippet shows the high-level method for fraction multiplication, which decomposes into multiply numerator and denominator.
```python
from shop2.domain import Method

fractMutl = Method(head=('fracMult', V('xn'), V('yn'), V('xd'), V('yd')),
                   preconditions=(Fact(field=V('xn'), value=V('vnx'))&
                                   Fact(field=V('yn'), value=V('vny'))&
                                   Fact(field=V('xd'), value=V('vxd'))&
                                   Fact(field=V('yd'), value=V('vyd'))),
                   subtasks=[Task('intMult', 'xn', 'yn', 'nom'), Task('intMult', 'xd', 'yd', 'denom')]
            ),
```

### Task
Consists of a head and flag for primitive status. It can either be primitive or non-primitive. The SHOP2 planner accepts a list of tasks as input.
```python
from shop2.domain import Task

solve = [Task('solve',)]
```

For further details refer to run.py.

## Planner
### Coroutine Planner
The coroutine planner waits for you to send some data to the generator. In order for the generator to terminate, it at StopException or FailedPlanException. Checkout run.py for more details.
```python
from shop2.planner import planner,
state = Fact(field='num_x', value=10)&Fact(field='den_x',value=12)
Tasks = [Task('fracAdd',)]
plan = planner(state, Tasks, Domain)
action_name, action_args = plan.send(None)
```

## Commands
```
python run.py
```

## Contact Information

For support, questions, or contributions, please contact us:

- **Email**: [msiddiqui66@gatech.edu](mailto:msiddiqui66@gatech.edu)
- **GitHub Issues**: [Submit Issue](https://github.com/Teachable-AI-Lab-TAIL/shop2/issues)
