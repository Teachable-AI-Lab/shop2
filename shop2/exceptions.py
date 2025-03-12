class StopException(Exception):
    """Exception raised for errors in the execution of a plan.

    Attributes:
        plan -- the plan that caused the error
        message -- explanation of the error
    """

    def __init__(self, plan=None, message="Task Completed"):
        self.plan = plan
        self.message = message
        super().__init__(self.message)

    def __str__(self):
        return f'{self.plan} -> {self.message}'


class FailedPlanException(Exception):
    """Exception raised for errors in the execution of a plan.

    Attributes:
        plan -- the plan that caused the error
        message -- explanation of the error
    """

    def __init__(self, plan=None, message="The plan execution failed"):
        self.plan = plan
        self.message = message
        super().__init__(self.message)

    def __str__(self):
        return f'{self.plan} -> {self.message}'


class GenericPlannerException(Exception):
    """
    A custom exception class used for miscellaneous errors.
    """

    def __init__(self, message=""):
        self.message = message
        super().__init__(self.message)

    def __str__(self):
        return self.message
