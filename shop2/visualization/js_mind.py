from collections import Counter
from json import dumps
from typing import Any
from typing import Dict
from typing import Generator
from typing import List
from typing import Optional
from typing import Set
from typing import Tuple
from typing import Union
from shop2.domain import Operator
from shop2.domain import Method


def get_jsmind_tree(network: Dict[str, List[Union[Method, Operator]]] = None,
                    task: str = None,
                    direction: str = "right") -> Dict[str, Any]:
    """

    :param network:
    :param task:
    :param direction:
    :return:
    """
    if task not in network:
        raise KeyError(f"Referenced task not found in network: {task}")
    # task, parent_id, display_name, node_type, node_id, details
    stack = [(task, None)]
    visited = set()
    node_array = [create_array_node(node_id=task,
                              parent_id=None,
                              is_root=True,
                              display_name=task.split("/")[0],
                              node_type='root',
                              direction=direction)]
    var_counter = Counter()

    while stack:
        # task_name, item_index parent_id, display_name, node_type
        current_task, parent_id = stack.pop(0)
        current_task_name = current_task.split('/')[0]
        visited.add(current_task)

        for item in network[current_task]:

            if isinstance(item, Method):
                item_id = f'{current_task_name}-M{var_counter[current_task_name]}'
                var_counter[current_task_name] += 1
                precond_str = str(item.preconditions) if item.preconditions else "None"
                details = f"Preconditions: {precond_str}\nSubtasks: {[str(t) for t in item.subtasks]}"

                node_array.append(create_array_node(node_id=item_id,
                                                    parent_id=parent_id if parent_id is not None else 'root',
                                              display_name=f'Method: {current_task_name}',
                                              node_type='method',
                                              direction=direction,
                                              details=details))
                for subtask in item.subtasks:
                    subtask_key = f'{subtask.name}/{len(subtask.args)}'
                    stack.append((subtask_key, item_id))
            else:
                item_id = f'{current_task_name}-OP{var_counter[current_task_name]}'
                var_counter[current_task_name] += 1
                effects_str = "\n".join(str(e) for e in item.effects)
                details = f"Effects:\n{effects_str}"
                node_array.append(create_array_node(node_id=item_id,
                                                    parent_id=parent_id if parent_id is not None else 'root',
                                              display_name=f'Operator: {current_task_name}',
                                              node_type='operator',
                                              direction=direction,
                                              details=details))
    with open('visualization.json', 'w') as file:
        file.write('[\n')
        for index, node in enumerate(node_array):
            file.write('\t' + dumps(node))
            if index < len(node_array) - 1:
                suffix = ',\n'
            else:
                suffix = '\n'
            file.write(suffix)

        file.write(']')
    return {
        "meta": {
            "name": "Domain Method/Operator Hierarchy",
            "author": "Python Script",
            "version": "1.0"
        },
        "format": "node_array",
        "data": node_array
    }


def create_array_node(node_id: str,
                parent_id: Any,
                display_name: str,
                node_type: str,
                direction: str,
                is_root: bool = False,
                children: Optional[List[Dict]] = None,
                details: Optional[str] = None
                ) -> Dict:
    """

    :param node_id:
    :param parent_id:
    :param display_name:
    :param node_type:
    :param direction:
    :param is_root:
    :param children:
    :param details:
    :return:
    """
    node = {
        "id": node_id,
        'parentid': parent_id,
        "topic": display_name,
        "direction": direction,
        "type": node_type
    }
    if is_root:
        node['isroot'] = True
    if children:
        node["children"] = children
    if details:
        node["details"] = details
    return node

