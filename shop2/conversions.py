from typing import Union
from shop2.conditions import AND
from shop2.conditions import OR
from shop2.fact import Fact


def logics_to_dicts_and_tuples(expression: (AND, OR)) -> (list, tuple):
    exp_type = OR() if isinstance(expression, OR) else AND()
    expression = list(expression)

    for index in range(len(expression)):
        if isinstance(expression[index], AND):
            expression[index] = logics_to_dicts_and_tuples(expression[index])
        elif isinstance(expression[index], OR):
            expression[index] = logics_to_dicts_and_tuples(expression[index])
        else:
            expression[index] = {k: expression[index][k] for k in expression[index]}

    if isinstance(exp_type, AND):
        return list(expression)
    elif isinstance(exp_type, OR):
        return tuple(expression)


def generate_logics(goals: Union[list, tuple]):
    """
    Converts a list of nested lists, tuples, and dictionaries into a logical expression.
    :param goals: (List) A list containing lists (representing an AND expression),
                  tuples (representing OR expressions), and dictionaries which are converted to Facts.
    :return: AND or OR expression
    """
    terms = []
    for index in range(len(goals)):
        if isinstance(goals[index], tuple):
            terms.append(OR(*generate_logics(goals[index])))
        elif isinstance(goals[index], list):
            terms.append(AND(*generate_logics(goals[index])))
        else:
            # Element is a dictionary
            terms.append(Fact(**goals[index]))
    return terms

