
from pycbc import transforms
from pycbc.distributions import bounded
from pycbc.workflow import configuration

class Constraint(object):
    name = "custom"
    required_name = []
    def __init__(self, variable_args, **kwargs):
        for kwarg in kwargs.keys():
            setattr(self, kwarg, kwargs[kwarg])
        _, self.transforms = transforms.get_conversions(
                                       self.required_parameters, variable_args)
        print self.transforms, self.required_parameters

    def __call__(self, params):
        params = transforms.apply_conversions(params, self.transforms) \
                     if self.transforms else params
        return self._constraint(params)

    def _constraint(self, params):
        return eval(self.func)

class MtotalLT(Constraint):
    name = "mtotal_lt"
    required_parameters = ["mass1", "mass2"]
    def _constraint(self, params):
        return params["mass1"] + params["mass2"] < self.mtotal

constraints = {
    Constraint.name : Constraint,
    MtotalLT.name : MtotalLT,
}
