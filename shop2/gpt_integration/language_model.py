from copy import deepcopy
from json import loads
from json.decoder import JSONDecodeError
import requests as req
from typing import Dict
from typing import List
from typing import Set
from typing import Tuple
from typing import Union
import anthropic
from shop2.conditions import AND
from shop2.conditions import OR
from shop2.conversions import generate_logics
from shop2.fact import Fact
from shop2.exceptions import GenericPlannerException
import yaml


class LanguageModel:
    def __init__(self, api_credentials: str):
        with open(api_credentials) as file:
            try:
                data = yaml.safe_load(file)
            except yaml.YAMLError as exc:
                raise Exception('Error loading API Credentials YAML file for language model.')
        self.api_key = data['api_key']
        self.service = data['service']
        self.model_version = data['model_version']
        self.url = data['url']
        self.prompts = loads(open('../../shop2/gpt_integration/prompts.json', 'r').read())

        if self.service == 'claud':
            __import__('anthropic')

    def explain_conditions(self, conditions: List[Dict], state: Dict, object_type: str):
        messages = deepcopy(self.prompts['explain_conditions']['messages'])
        messages[0]['content'] = messages[0]['content'].format(object_type.lower(),
                                                               object_type.lower(),
                                                               conditions,
                                                               state)
        return self._send(request_type='explain_conditions', messages=messages)

    def generate_goal_conditions(self, state: Dict, user_statement: str):
        messages = deepcopy(self.prompts['generate_goals']['messages'])
        messages[0]['content'] = messages[0]['content'].format(state, user_statement)
        resp = self._send(request_type='generate_goals', messages=messages)
        return self._generate_goal_conditions(resp, user_statement)

    def _send(self, request_type: str, messages: List[Dict], max_tokens=1024):
        if self.service == 'claud':
            request_context = self.prompts[request_type].get('request_context') \
                if self.prompts[request_type].get('request_context') else ''
            headers = {
                'x-api-key': self.api_key,
                'anthropic-version': '2023-06-01',
                'content-type': 'application/json'
            }
            data = {
                'model': self.model_version,
                'max_tokens': max_tokens,
                'messages': messages,
                'system': request_context
            }
            resp = req.post(self.url, headers=headers, json=data)
            return resp.json()['content'][0]['text']

    @staticmethod
    def _generate_goal_conditions(language_model_output: str, user_statement: str) -> Union[AND, OR]:
        delimiter = 'Answer:'
        if language_model_output.find(delimiter) == -1:
            raise GenericPlannerException(f'Planner could not generate a goal from user statement {user_statement}')
        try:
            output = language_model_output.split('Answer:')[-1].strip()
            goals = loads(output)
        except JSONDecodeError:
            raise GenericPlannerException(f'Planner could not generate a goal from user statement {user_statement}')

        return generate_logics(goals)[0]





