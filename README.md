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
Axiom(head=('value-equality', '?x', '?y'), 
      conditions=[('value', '?x', '?v'), ('value', '?y', '?v'), (lambda x, y: x<y, '?x', '?y')])
```

### Operator
Consists of head, conditions, and effects. Delete effects are discerned by using the 'not' keyword in the predicate. Use lambda or normal functions for executing the operator on the bound variables. 
```python
from shop2.domain import Operator
"intAdd": Operator(head=('intAdd', '?x', '?y', '?z'),
                        conditions=[('value', '?x', '?vx'), ('value', '?y', '?vy')],
                        effects=[('value', '?z', (lambda x,y: x+y, '?vx', '?vy'))]),
```

## Commands
```
python run.py
```
