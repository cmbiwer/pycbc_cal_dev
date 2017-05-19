from pycbc import transforms
from pycbc.distributions import bounded
from pycbc.workflow import configuration

class Constraint(object):
    """ Creates a constraint that evaluates to True if parameters obey
    the constraint and False if they do not.
    """
    name = "custom"
    required_name = []
    def __init__(self, variable_args, **kwargs):
        for kwarg in kwargs.keys():
            setattr(self, kwarg, kwargs[kwarg])
        _, self.transforms = transforms.get_conversions(
                                       self.required_parameters, variable_args)

    def __call__(self, params):
        """ Evaluates constraint.
        """
        params = transforms.apply_conversions(params, self.transforms) \
                     if self.transforms else params
        return self._constraint(params)

    def _constraint(self, params):
        """ Evaluates constraint function.
        """
        return eval(self.func)

class MtotalLT(Constraint):
    """ Pre-defined constraint that check if total mass is less than a value.
    """
    name = "mtotal_lt"
    required_parameters = ["mass1", "mass2"]
    def _constraint(self, params):
        """ Evaluates constraint function.
        """
        return params["mass1"] + params["mass2"] < self.mtotal

# list of all constraints
constraints = {
    Constraint.name : Constraint,
    MtotalLT.name : MtotalLT,
}

