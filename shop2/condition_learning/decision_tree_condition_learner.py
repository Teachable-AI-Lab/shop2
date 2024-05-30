from itertools import combinations
# from typing import
from typing import Dict
from random import choice
from random import seed
from random import shuffle

from refactor.tilde_essentials.example import Example
from refactor.tilde_essentials.leaf_strategy import LeafBuilder
from refactor.tilde_essentials.splitter import Splitter
from refactor.tilde_essentials.stop_criterion import StopCriterion
from refactor.tilde_essentials.evaluation import TestEvaluator
from refactor.tilde_essentials.test_generation import TestGeneratorBuilder
from refactor.tilde_essentials.tree import DecisionTree
from refactor.tilde_essentials.tree_builder import TreeBuilder


class DTConditionLearner:
    def __init__(self, num_trees=1, shuffle_instances=False, random_seed=None):
        self.instances = []
        self.num_trees = num_trees
        self.decision_trees = [None] * self.num_trees
        self.shuffle_instances = shuffle_instances
        if random_seed is not None and self.shuffle_instances:
            seed(random_seed)

        # Decision tree settings
        self.test_evaluator = DTTestEvaluator()

        self.test_generator_builder = DTTestGenerator()

        self.splitter = Splitter(split_criterion_str='entropy',
                                 test_evaluator=self.test_evaluator,
                                 test_generator_builder=self.test_generator_builder,
                                 verbose=True)
        self.stop_criterion = StopCriterion()

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
        print(f"Num outcomes: {len(outcomes)}")
        if all([outcomes.count(label) == outcomes.count(labels[0]) for label in labels]):
            print("giving random match")
            return choice(labels)
        else:
            print("not random match")
            return max(set(outcomes), key=outcomes.count)

    def _fit(self, instance, is_positive):
        self.instances.append(Example(data=instance, label=is_positive))
        self._build_decision_trees()

    def _build_decision_trees(self):
        leaf_builder = LeafBuilder()

        tree_builder = TreeBuilder(splitter=self.splitter,
                                   leaf_builder=leaf_builder,
                                   stop_criterion=self.stop_criterion)
        if self.shuffle_instances:
            shuffle(self.instances)
        for i in range(self.num_trees):
            self.decision_trees[i] = DecisionTree()
            self.decision_trees[i].fit(examples=self.instances,
                                       tree_builder=tree_builder)


class DTTestEvaluator(TestEvaluator):
    def evaluate(self, example, test) -> bool:
        return example in test[0]
        # print("test: ", test)
        # return choice([True, False])
        # return True
        # x = choice([True, False])
        # print("returning ", x, " label: ", example.label)
        # return x


class DTTestGenerator(TestGeneratorBuilder):
    """
    Builds a generator to produce possible tests in a node to be split.

    """
    def generate_possible_tests(self, examples, current_node):
        for split in self._create_splits(examples):
            yield split

    @staticmethod
    def _create_splits(examples):
        combos = []
        for i in range(1, len(examples)):
            combos += combinations(examples, i)

        result = []
        for c1 in combos:
            curr = list(c1)
            for c2 in combos:
                combo = (tuple(curr), tuple(c2))
                if not any(i in curr for i in c2) and \
                        (len(curr) + len(c2) == len(examples)) and \
                        set(combo) not in result:
                    result.append(set(combo))
        return [list(i) for i in result]

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
    dt = DTConditionLearner(num_trees=10, shuffle_instances=True)
    count = 1
    for e in examples:
        print("FITTING EXAMPLE  ", count)
        count+=1
        if e[1]:
            dt.generalize(e[0])
        else:
            dt.specialize(e[0])
    print(dt.decision_trees[0].tree_builder.tree_root)
    print(dt.decision_trees[0].tree.depth)
    scores = []
    for i in range(len(examples)):
        pred = dt.match(examples[i][0])
        scores.append(1 if pred == examples[i][1] else 0)
        print("predicted example: ", pred)

    x = {"1.color": "Red", "1.size": "Large", "2.shape": "Circle", "2.color": "Blue",
         "2.size": "Small"}
    pred = dt.match(x)
    print("predicted example: ", pred)
    scores.append(1 if pred == True else 0)
    print(f"Final Score with ({dt.num_trees}) trees: {round(sum(scores)/len(scores)*100, 2)}%")
"""