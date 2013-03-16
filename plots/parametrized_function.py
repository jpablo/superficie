from functools import partial


def getExtraVariables(func):
    # the first 2 names are the regular function arguments R^2 -> R^3
    # names in positions beyond func.func_code.co_argcount are local variables, so we discard it
    return [v for v in func.func_code.co_varnames[2:func.func_code.co_argcount] if v not in ('args', 'kwargs')]


def noop(self, values=None):
    pass


class ParametrizedFunction(object):
    def __init__(self, func, extraVars=()):
        self.func = func
        self.extraVariables = getExtraVariables(func) or extraVars
        # if no extra variables detected, no need to wrap the original function
        if not self.extraVariables:
            self.updateExtraVariables = noop
            self.partial = self.func

        self.updateExtraVariables(self.defaultValues())

    def __call__(self, *args, **kwargs):
        return self.partial(*args, **kwargs)

    def updateExtraVariables(self, values=None):
        if not values:
            values = {}
        self.partial = partial(self.func, **values)

    def defaultValues(self):
        return dict([(var, 0) for var in self.extraVariables])

    def argCount(self):
        return self.func.func_code.co_argcount

