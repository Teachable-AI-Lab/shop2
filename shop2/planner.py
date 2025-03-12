from copy import deepcopy
from itertools import chain, permutations
from random import choice
from time import sleep
from typing import Dict
from typing import Generator
from typing import List
from typing import Set
from typing import Tuple
from typing import Union
# from shop2.gpt_integration.language_model import LanguageModel
from shop2.domain import Task, Axiom, Method, flatten, Operator
from shop2.utils import replaceHead, replaceTask, removeTask, generatePermute
from shop2.fact import Fact
from shop2.conditions import AND
from shop2.exceptions import FailedPlanException
from shop2.exceptions import StopException
from shop2.validation import validate_domain
from shop2.validation import validate_state
from shop2.validation import validate_tasks


class Planner:
    def __init__(self,
                 tasks: List,
                 domain: Dict,
                 validate_input: bool = False,
                 repeat_wait_time: int = 5,
                 order_by_cost: bool = False,
                 logging: bool = False,
                 log_dir: str = None):
        # self._validate_inputs(state, tasks, domain)
        if validate_input:
            validate_domain(domain)
            # validate_state(state)
            validate_tasks(tasks)

        self.coroutine = None
        self.state = None
        self.tasks = []
        self.domain = domain

        # Working memory
        self.wm = []
        self.plan = []
        self.plan_sequence_counter = 0
        # Planner options
        self.validate = validate_input
        self.repeat_wait_time = repeat_wait_time
        self.order_by_cost = order_by_cost
        self.logging = logging
        self.log_dir = log_dir if log_dir is not None else 'pyHTN-logger.log.'
        # self.explanations = explanations
        # self.visualize = visualize
        # self.language_model = LanguageModel('../../shop2/gpt_integration/api_credentials.yaml')

        self._add_tasks(tasks)

    def update(self, info: dict = None):
        if self.coroutine is None:
            self.state = info.get('state')
            if self.validate:
                validate_state(self.state)
            self.coroutine = self._plan()
            return next(self.coroutine)

        return self.coroutine.send(info)

    def explain(self, decision: 'PlanAction'):
        return self.language_model.explain_conditions(decision.preconditions, decision.state, decision.type)

    def get_current_plan(self):
        return self.plan

    def stop(self):
        # _ = self.coroutine({'stop': True})
        self.coroutine = None
        print('Planner Stopped.')

    def visualize(self, what_to_visualize='plan'):
        pass

    def _plan(self):
        # plan = []
        # stack, inner_visited, outer_visited = [], [], []
        # print('tasks: ', self.tasks)
        while True:
            if not self.tasks:
                raise StopException('There are no tasks.')
            # Gets either a single task or a set of partially ordered task (i.e. can be solved in any order)
            task_group = self._get_new_task(self.tasks)
            task = choice(task_group)

            self.plan = []
            stack, inner_visited, outer_visited = [], [], []
            # print('did something')
            success = False
            # Determines which set of methods/operators to explore
            domain_key = f"{task.name}/{len(task.args)}"
            options = self.domain[domain_key] if not self.order_by_cost \
                else sorted(self.domain[domain_key], key=lambda op: op.cost)

            for option in options:
                print('option: ', option)
                print(type(option))
                if isinstance(option, Operator):
                    if result := option.applicable(task, self.state):
                        # TODO if task repeats, should the plan reflect that or should it only track it once
                        self._add_plan_action(domain_key, option, self.state, result['matched_facts'])
                        info = yield result  # self._generate_response(result, self.plan)

                        success = self._process_response(info)

                        if success:

                            # self.tasks = self._remove_task(self.tasks, task)
                            # print('Task successful. plan: ', plan)
                            if task.repeat:
                                print(f"Task should repeat. Resuming after {self.repeat_wait_time} seconds.")
                                sleep(self.repeat_wait_time)
                            else:
                                self._remove_task(self.tasks, task)
                        else:
                            self.plan.pop()
                        break

                elif isinstance(option, Method):
                    # option is applicable if state can be unified with method preconditions
                    if result := option.applicable(task, self.state, str(self.plan), inner_visited):
                        stack.append((deepcopy(self.tasks), deepcopy(self.plan), deepcopy(self.state)))
                        subtask = result
                        # T = type(T)([subtask]) + removeTask(T, task)
                        self.tasks = [subtask] + self._remove_task(self.tasks, task)
                        success = True
                        self._add_plan_action(option, self.state)
                        break

                option_info = (str(option.head), str(option.preconditions), str(self.state))
                if option_info in outer_visited:
                    break
                else:
                    outer_visited.append(option_info)

            if not success:
                if stack:
                    self.tasks, plan, state = stack.pop()
                    self.plan.pop()
                    # state = AND(*flatten(state))
                else:
                    if task.repeat:
                        print(f'Task not successful. Will repeat after {self.repeat_wait_time} seconds.')
                        sleep(self.repeat_wait_time)
                        continue
                    # Otherwise, raise exception
                    raise FailedPlanException(message="No valid plan found")

    def _add_plan_action(self, task, action_object: Union[Operator, Method], state: List[Dict], matched_facts: AND):
        self.plan.append(PlanAction(sequence_id=self.plan_sequence_counter,
                                    task=task,
                                    state=state,
                                    action_object=action_object,
                                    matched_facts=matched_facts))
        self.plan_sequence_counter += 1

    def _validate_inputs(self, state, tasks, domain):
        if not self.tasks:
            raise StopException()

    def _process_response(self, info: Dict):
        # Validate
        # must have success
        # must have state
        # can have new tasks.
        #   tasks can have priority (low, med, high)
        #   can set tasks to recurse -done
        # can erase old tasks and assign new ones
        # can pass in options for other functions to run before progressing
        # TODO add unless conditions
        #   used to skip tasks when their effects already present
        #   can be used to control ordering of Tasks
        # TODO add effects -done
        success = info.get('success')
        if success is None:
            raise KeyError("Parameter 'success' is missing from input dictionary.")

        state = info.get('state')
        if state is None:
            raise KeyError("Parameter 'state' is missing from input dictionary.")

        if info.get('tasks') is not None:
            self._add_tasks(info['tasks'])
        # Passed
        self.state = state
        return success

    def _generate_response(self, effects: List[Fact], plan: List):
        resp = {
            'effects': effects,
            'stopped': False
        }
        return resp

    def _add_tasks(self, tasks: List[Union[str, Tuple, Dict]]):
        """
        Converts a list of task specifications into Task objects.
        :param tasks: List of tasks where each task can be:
                - str: Simple task name
                - tuple: (task_name, *args)
                - dict: {task: str/tuple,
                         priority: 'low'/'medium'/'high',
                         repeat: bool}
        :return: None
        """
        if self.validate:
            # First validate all tasks
            validate_tasks(tasks)

        for t in tasks:
            # Strings
            if isinstance(t, str):
                self.tasks.append(Task(t))

            # Dictionaries
            else:
                task = t['task']
                args = t.get('arguments') if t.get('arguments') else ()
                priority = t.get('priority') if t.get('priority') else 'low'
                repeat = t.get('repeat') if t.get('repeat') else False

                new_task = Task(task, args=args, priority=priority, repeat=repeat)

                if priority in [0, 'first']:
                    self.tasks.insert(0, new_task)
                else:
                    self.tasks = self._add_task(new_task, self.tasks)

    def _add_task(self, new_task: Task, tasks: List):
        if not tasks:
            return [new_task]
        for i in range(len(tasks)):
            if isinstance(tasks[i], (list, tuple)):
                tasks[i] = self._add_task(new_task, tasks[i])
            else:
                if new_task.priority <= tasks[i].priority:
                    # TODO decide if new tasks can be added with partially ordered tasks or must strictly come before
                    #   or after
                    if isinstance(tasks, tuple):
                        tasks = (*tasks[:i], new_task, *tasks[i:])
                    else:
                        tasks.insert(i, new_task)
                    return tasks
        return tasks

    def _get_new_task(self, tasks: Union[List, Tuple]) -> Union[List, Tuple]:
        """
        Returns list/tuple of tasks which no other task in T is constrained to precede.
        """
        # print('tasks list in get new task: ', tasks)
        if isinstance(tasks, list) and not isinstance(tasks[0], (list, tuple)):
            return [tasks[0]]
        elif isinstance(tasks, list):
            return self._get_new_task(tasks[0])
        elif isinstance(tasks, tuple):
            return tuple(chain.from_iterable(self._get_new_task(t)
                                             if isinstance(t, (list, tuple)) else (t,) for t in tasks))

    def _remove_task(self, tasks: Union[List, Tuple], task: Task) -> Union[List, Tuple]:
        """
        Removes task 'task' from a list or tuple of tasks.
        """
        if isinstance(tasks, list):
            return [result for t in tasks if (result := self._remove_task(t, task)) != task and result]
        elif isinstance(tasks, tuple):
            return tuple(result for t in tasks if (result := self._remove_task(t, task)) != task and result)
        else:
            return tasks

    def _save_logs(self):
        if self.logging:
            for p in self.plan:
                pass



    @staticmethod
    def _print_plan(plan: List):
        return str(plan)




class PlanAction:
    def __init__(self, sequence_id: int,
                 task: str,
                 state: List[dict],
                 action_object: Union[Operator, Method],
                 matched_facts):
        self.id = sequence_id
        self.task = task
        if isinstance(action_object, Operator):
            self.type = 'Operator'
            self.output = action_object.effects
        else:
            self.type = 'Method'
            self.output = [str(subtask) for subtask in action_object.subtasks]

        self.name = action_object.name
        self.args = action_object.args
        self.preconditions = action_object.preconditions
        self.state = deepcopy(state)
        self.matched_facts = matched_facts

    def __str__(self):
        return self._print_str()

    def __repr__(self):
        return self._print_str()

    def get_log_record(self):
        return {
            'sequence_id': self.id,
            'task': self.task,
            'type': self.type,
            'name': self.name,
            'args': list(self.args),
            'preconditions': ''

        }

    def _print_str(self):
        return f"{self.type}(sequence={self.id}, name={self.name}, args={self.args})"







                

