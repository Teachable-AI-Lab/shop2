# from typing import
from typing import Dict
from random import choice
from random import seed

from tilde_essentials.example import Example
from tilde_essentials.leaf_strategy import LeafBuilder
from tilde_essentials.splitter import Splitter
from tilde_essentials.stop_criterion import StopCriterion
from tilde_essentials.evaluation import TestEvaluator
from tilde_essentials.test_generation import TestGeneratorBuilder
from tilde_essentials.tree import DecisionTree
from tilde_essentials.tree_builder import TreeBuilder


class DTConditionLearner:
    def __init__(self, num_trees=1):
        self.instances = []
        self.num_trees = num_trees
        self.decision_trees = [None] * self.num_trees

        # Decision tree settings
        self.test_evaluator = DTTestEvaluator()

        self.test_generator_builder = DTTestGenerator()

        self.splitter = Splitter(split_criterion_str='entropy',
                                 test_evaluator=self.test_evaluator,
                                 test_generator_builder=self.test_generator_builder)
        self.stop_criterion = StopCriterion()
        seed(0)

    def generalize(self, instance):
        self._fit(instance, True)

    def specialize(self, instance):
        self._fit(instance, False)

    def match(self, instance):
        if not self.decision_trees:
            raise Exception("You must fit at least one example into decision tree before predicting a value.")
        ex = Example(data=instance, label=None)
        labels = [True, False]
        outcomes = [dt.predict(ex) for dt in self.decision_trees]
        if all([outcomes.count(label) == outcomes.count(labels[0]) for label in labels]):
            return choice(labels)
        else:
            return max(set(outcomes), key=outcomes.count)

    def _fit(self, instance, is_positive):
        self.instances.append(Example(data=instance, label=is_positive))
        self._build_decision_trees()

    def _build_decision_trees(self):
        leaf_builder = LeafBuilder()

        tree_builder = TreeBuilder(splitter=self.splitter,
                                   leaf_builder=leaf_builder,
                                   stop_criterion=self.stop_criterion)
        for i in range(self.num_trees):
            self.decision_trees[i] = DecisionTree()
            self.decision_trees[i].fit(examples=self.instances,
                                       tree_builder=tree_builder)


class DTTestEvaluator(TestEvaluator):
    def evaluate(self, example, test) -> bool:
        # print("test: ", test)
        return choice([True, False])
        # return True
        # x = choice([True, False])
        # print("returning ", x, " label: ", example.label)
        # return x


class DTTestGenerator(TestGeneratorBuilder):
    """
    Builds a generator to produce possible tests in a node to be split.

    """
    def generate_possible_tests(self, examples, current_node):
        yield current_node.test

"""
if __name__ == "__main__":
    examples = [
        ({"1.shape": "Circle", "1.color": "Blue", "1.size": "Large", "2.shape": "Triangle", "2.color": "Red",
         "2.size": "Large"}, True),
        ({"1.shape": "Triangle", "1.color": "Blue", "1.size": "Large", "2.shape": "Triangle", "2.color": "Blue",
         "2.size": "Large"}, True),
        ({"1.shape": "Triangle", "1.color": "Blue", "1.size": "Large", "2.shape": "Triangle", "2.color": "Blue",
         "2.size": "Small"}, False),
        ({"1.shape": "Triangle", "1.color": "Red", "1.size": "Large", "2.shape": "Circle", "2.color": "Blue",
         "2.size": "Small"}, True),
        ({"1.shape": "Circle", "1.color": "Blue", "1.size": "Large", "2.shape": "Triangle", "2.color": "Blue",
         "2.size": "Large"}, False)
    ]
    dt = DTConditionLearner()
    count = 1
    for e in examples:
        print("FITTING EXAMPLE  ", count)
        count+=1
        dt.fit(*e)
    print(dt.decision_trees[0].tree_builder.tree_root)
    print(dt.decision_trees[0].tree.depth)
    print("predicted example: ", dt.predict(examples[0][0]))
    print("predicted example: ", dt.predict(examples[1][0]))
    print("predicted example: ", dt.predict(examples[2][0]))
    print("predicted example: ", dt.predict(examples[3][0]))
    print("predicted example: ", dt.predict(examples[4][0]))
"""