from copy import deepcopy
from json import dumps
from typing import Dict
from typing import Generator
from typing import List, Any, Optional
from typing import Set
from typing import Tuple
from typing import Union
from shop2.domain import Task, Operator, Method
from shop2.planner import Planner
from shop2.exceptions import FailedPlanException
from shop2.exceptions import GenericPlannerException
from shop2.exceptions import StopException
from shop2.fact import Fact
from shop2.common import V
from shop2.conditions import Filter, NOT

domain = {
    "solve/0": [
        Method(head=('solve',),
               preconditions=(Fact(field='op', operator='*') &
                              Fact(field='xn', value=V('vnx')) &
                              Fact(field='yn', value=V('vny')) &
                              Fact(field='xd', value=V('vdx')) &
                              Fact(field='yd', value=V('vdy'))),
               subtasks=[Task('multiply_numerators'), Task('multiply_denominators')]
               ),
        Method(head=('solve',),
               preconditions=(Fact(field='op', operator='*') &
                              Fact(field='xn', value=V('vnx')) &
                              Fact(field='yn', value=V('vny')) &
                              Fact(field='xd', value=V('vdx')) &
                              Fact(field='yd', value=V('vdy'))),
               subtasks=[Task('multiply_denominators'), Task('multiply_numerators')]
               )

    ],
    "solve/2": [
        Method(head=('solve', 'a', 'b'),
               preconditions=(Fact(field='op', operator='*') &
                              Fact(field='xn', value=V('vnx')) &
                              Fact(field='yn', value=V('vny')) &
                              Fact(field='xd', value=V('vdx')) &
                              Fact(field='yd', value=V('vdy'))),
               subtasks=[Task('multiply_numerators'), Task('multiply_denominators')]
               )

    ],
    "multiply_numerators/0": [
        Method(head=('multiply_numerators',),
               preconditions=(Fact(field='op', operator='*') &
                              Fact(field='xn', value=V('vxn')) &
                              Fact(field='yn', value=V('vyn'))),
               subtasks=[Task('multiply', (V('vxn'), V('vyn'))), Task('input_value')]
               ),
    ],
    "multiply_denominators/0": [
        Method(head=('multiply_denominators',),
               preconditions=(Fact(field='op', operator='*') &
                              Fact(field='xd', value=V('vxd')) &
                              Fact(field='yd', value=V('vyd'))),
               subtasks=[Task('multiply', (V('vxd'), V('vyd'))), Task('input_value')]
               ),
    ],
    "multiply/2": [
        Operator(head=('multiply', V('a'), V('b')),
                 preconditions=(),
                 effects=[Fact(type='memory', result=lambda a, b: a * b)]
                 )
    ],
    "add/2": [
        Operator(head=('add', V('a'), V('b')),
                 preconditions=(),
                 effects=[Fact(type='memory', result=lambda a, b: a + b)]
                 )
    ],
    "input_value/0": [
        Operator(head=('input_value', V('a'), V('b')),
                 preconditions=(),
                 effects=[Fact(type='sai', selection=V('b'), action='input_value', input=V('a'))]
                 )
    ]
}


class HTNVisualizer:
    def __init__(self, network: Dict[str, List[Union[Method, Operator]]]):
        self.network = network


class JSMindVisualizer:
    mind = {
        "meta": {
            "name": "example",
            "author": "hizzgdev@163.com",
            "version": "0.2"
        },
        "format": "node_array",
        "data": [
            {"id": "root", "isroot": True, "topic": "jsMind"},

            {"id": "easy", "parentid": "root", "topic": "Easy", "direction": "left"},
            {"id": "easy1", "parentid": "easy", "topic": "Easy to show"},
            {"id": "easy2", "parentid": "easy", "topic": "Easy to edit"},
            {"id": "easy3", "parentid": "easy", "topic": "Easy to store"},
            {"id": "easy4", "parentid": "easy", "topic": "Easy to embed"},

            {"id": "open", "parentid": "root", "topic": "Open Source", "direction": "right"},
            {"id": "open1", "parentid": "open", "topic": "on GitHub"},
            {"id": "open2", "parentid": "open", "topic": "BSD License"},

            {"id": "powerful", "parentid": "root", "topic": "Powerful", "direction": "right"},
            {"id": "powerful1", "parentid": "powerful", "topic": "Base on Javascript"},
            {"id": "powerful2", "parentid": "powerful", "topic": "Base on HTML5"},
            {"id": "powerful3", "parentid": "powerful", "topic": "Depends on you"},
        ]
    }



#js_mind_map = convert_domain_to_jsmind(domain, "solve/0")
#with open('../../examples/js_mind_map.jm', 'w') as file:
#    file.write(dumps(js_mind_map, indent=2))
