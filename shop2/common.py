from dataclasses import dataclass
"""
    TODO:
        - Why is fields at the top? is it mutable?
            - seems to be used in other functions to get the field names
"""

variable_counter = 0


def gen_variable():
    global variable_counter
    variable_counter += 1
    return V('genvar{}'.format(variable_counter))


@dataclass(eq=True, frozen=True)
class V:
    """
    A variable for pattern matching.
    """
    name: str

    def to_unify_str(self):
        return f"?{ self.name }"

# class V:
#     """
#     A variable for pattern matching.
#     """

#     def __init__(self, name):
#         self.name = name

#     def __repr__(self):
#         return "V({})".format(self.name)

#     def __hash__(self):
#         return hash("V({})".format(self.name))

#     def __eq__(self, other):
#         if not isinstance(other, V):
#             return False
#         return self.name == other.name

