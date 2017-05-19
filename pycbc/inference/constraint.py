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

class EffectiveSpinSpace(Constraint):
    """ Pre-defined constraint that check if effective spin parameters
    are within accpetable values.
    """
    name = "effective_spin_space"
    required_parameters = ["mass1", "mass2", "q", "xi1", "xi2",
                           "chi_eff", "chi_a"]

    def _constraint(self, params):
        """ Evaluates constraint function.
        """

        # ensure that mass1 > mass2
        if params["mass1"] < params["mass2"]:
            return False

        # constraint for primary mass
        a = ((4.0 * params["q"]**2 + 3.0 * params["q"])
                 / (4.0 + 3.0 * params["q"]) * params["xi1"])**2
        b = ((1 + params["q"]**2) / 4
                 * (params["chi_eff"] + params["chi_a"])**2)
        if a + b > 1:
            return False

        # constraint for secondary mass
        a = params["xi2"]**2
        b = ((1 + params["q"]**2) / (4 * params["q"]**2)
                 * (params["chi_eff"] - params["chi_a"])**2)
        if a + b > 1:
            return False

        return True


# list of all constraints
constraints = {
    Constraint.name : Constraint,
    MtotalLT.name : MtotalLT,
    EffectiveSpinSpace.name : EffectiveSpinSpace,
}

