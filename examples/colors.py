from shop2.domain import Task, Operator, Method
from shop2.planner import Planner, StopException, FailedPlanException
from shop2.fact import Fact
from shop2.common import V
from shop2.conditions import Filter, NOT


def change_color(c):
    color_map = {'blue': 'yellow', 'red': 'cyan', 'green': 'magenta'}
    # print(f'Changing color from ({c}) to ({color_map[c]})')
    return color_map[c]


domain = {
    "change_color/0": [
        Operator(
            head=('change_color',),
            preconditions=Fact(shape='triangle', color=V('color')),
            effects=[Fact(new_color=(lambda c: change_color(c), V('color')))]
        )
    ]
}

state = [
    {'shape': 'triangle', 'color': 'blue', 'id': 1},
    {'shape': 'square', 'color': 'red', 'id': 2}
]

tasks = [{'task': 'change_color', 'repeat': False}]

planner = Planner(domain=domain, tasks=tasks, repeat_wait_time=5)
result = planner.update()
####
current_plan = planner.get_current_plan()
print('Output of first operator: ', result)
print('Plan: ', current_plan)
print('Explanation of first step in plan: ', planner.explain(current_plan[0]))
####

info = {'success': True, 'state': state}

while True:
    result = planner.update(info)
    break
    # print('result: ', result)

