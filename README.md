# Python SHOP2

![Build Status](https://github.com/Teachable-AI-Lab-TAIL/shop2/workflows/Build/badge.svg)

## Overview

This project implements [SHOP2 (Simple Hierarchical Ordered Planner No. 2)](https://www.cs.umd.edu/~nau/papers/nau2003shop2.pdf) in Python. SHOP2 is a powerful hierarchical task network (HTN) planning system known for its efficiency and effectiveness in handling a variety of planning domains. While SHOP2 was originally designed to directly modify world states during planning (closed-world assumption), this implementation only suggests actions for external programs to execute (open-world). It receives updated states after each action, allowing it to adapt its plan as needed.

## Features
- **Horn Clause Inference Engine**: Utilizes a Horn clause logic system, allowing for efficient and logical problem-solving capabilities.
- **Partial Ordering**: Using tuples (unordered) and lists (ordered), the system represents partial ordering within the plan.
- **Facts**: Supports a Fact notation. For an overview of facts, review [this link](https://github.com/cmaclell/py_rete). Note that the conditions described in the "Productions" section is analogous to preconditions described in this project and so the functionality is the same.

## Prerequisites

- Python version >= 3.8

## Installation 
Clone the repository using the following command:
```
git clone https://github.com/Teachable-AI-Lab-TAIL/shop2.git
```
Alternatively, install the repository using pip with the following command:
```
pip install git+https://github.com/Teachable-AI-Lab-TAIL/shop2.git
```

## Domain Description
A domain description describes a planning domain and consists of a set of methods and operators and/or axioms, all indexed by the task they help achieve. 

### Task
Task objects are used to link together the various compents of the HTN. Tasks consist of a task name and an optional set of arguments.

This example shows a simple task for multiplying two fractions. It only specifies a name and takes no arguments.
```python
from shop2.domain import Task

solve_task = Task('fraction_mult',)
```

This example shows a task for adding two numbers. It specifies a name and takes three variablized arguments, namely the field names containing the numbers to be added (a and b) and the field name of the answer box to put the result in.
```python
from shop2.domain import Task

add_task = Task('add', V('a'), V('b'), V('c'))
```

### Method
Methods are what add hierarchy to HTNs and decompose tasks into subtasks. Methods consists of a _head_, a set of _preconditions_, and a list of _subtasks_. The head defines the task the method achieves as well as any arguments to be passed in. The preconditions define a set of _Facts_ that must be true in the world state for this method to be applicable. Finally, subtasks are represented by a list of Task objects.

The below example shows a method for completing a fraction multiplication problem where there are two fraction operands. We see that the method decomposes the task of solving a fraction multiplcation problem into the two tasks of multiplying the numerators and then the denominators, respectively. 
```python
from shop2.common import V
from shop2.domain import Method
from shop2.fact import Fact

fraction_mult_method = Method(head=('fraction_mult', V('num1'), V('num2'), V('denom1'), V('denom2')),
                              preconditions=(Fact(field=V('num1'), value=V('num1_val'))&
                                             Fact(field=V('num2'), value=V('num2_val'))&
                                             Fact(field=V('denom1'), value=V('denom1_val'))&
                                             Fact(field=V('denom2'), value=V('denom2_val'))),
                              subtasks=[Task('multiply', 'num1', 'num2', 'ans_num'), Task('multiply', 'denom1', 'denom2', 'ans_denom')]
            ),
```

### Operator
Operators define the fundamental actions the planning system can take. Operators consist of a head, a set of preconditions, and a set of _effects_ that result from the application of an operator. The effects, in this implementation, are currently not used but will be revisited in the near future.

The below example shows an HTN operator for multiplying two numbers in a web-based, tutoring system interface. The operator expects 3 variablized arguments: f1 and f2 (the field names containing the two values to multiply) and f3 (the field name of the interface element to put the result). The preconditions will match against the two fields in the tutor interface (f1 and f2) and their corresponding values (vf1 and vf2). The effects use these bindings to calculate the result of the multiplication and return this as an effect. 
```python
from shop2.common import V
from shop2.domain import Operator
from shop2.fact import Fact

multiply_op = Operator(head=('multiply', V('f1'), V('f2'), V('f3')),
                       preconditions=(Fact(field=V('f1'), value=V('vf1'))&
                                      Fact(field=V('f2'), value=V('vf2'))),
                       effects=Fact(field=V('f3'), value=(lambda x,y: x*y, V('vf1'), V('vf2')))),
```

### Axioms
Axioms are implemented but not currently documented. See shop2/domain.py.


In this project, the domain description is represented by a dictionary where the keys specify tasks and the number of arguments (e.g. `multiply/2`) and the values are a list of relevant methods or operators. For an example of a domain and additional examples of tasks, methods, and operators, refer to [run.py](https://github.com/Teachable-AI-Lab/shop2/blob/main/run.py). 


## Planner
The planner runs as a coroutine in a separate process. Given an initial state, domain, and tasks, it iteratively suggests operators and their argument bindings. The driver program applies these to the environment and returns the resulting state to the planner. This continues until either all tasks are completed (resulting in a `StopException`) or no valid plan can be found (resulting in a `FailedPlanException`).

```python
from shop2.planner import planner

domain = {
        "add/0": [
            Operator(head=('add', V('a'), V('b'), V('c')),
                     preconditions=(Fact(field=V('a'), value=V('va')) &
                                    Fact(field=V('b'), value=V('vb'))),
                     effects=Fact(field=V('c'), value=(lambda x, y: x + y, V('va'), V('vb')))),

        ]
    }
state = Fact(field='operand1', value=10) & Fact(field='operand2', value=12) & Fact(field='answer_box', value=)
tasks = [Task('add',)]
plan = planner(state, tasks, domain)

action_name, action_args = plan.send(None)

# At this point, the driver program would need to do the addition and apply it to the environment. However, in the near future the planner will support performing these operations directly in the effects and returning them to the driver.
action_name -> add
action_args -> (10, 12, null)
```

## Commands
```
python run.py
```

## Contact Information

For support, questions, or contributions, please contact us:

- **Email**: [msiddiqui66@gatech.edu](mailto:msiddiqui66@gatech.edu)
- **GitHub Issues**: [Submit Issue](https://github.com/Teachable-AI-Lab-TAIL/shop2/issues)
