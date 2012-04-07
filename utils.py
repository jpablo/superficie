__author__ = 'jpablo'

def fluid(method):
    """
    Fluiditize a method
    """
    def func(self, *args, **kwargs):
        method(self,*args, **kwargs)
        return self
    return func