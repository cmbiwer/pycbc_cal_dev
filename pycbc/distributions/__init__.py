# Copyright (C) 2016  Collin Capano, Christopher M. Biwer
# This program is free software; you can redistribute it and/or modify it
# under the terms of the GNU General Public License as published by the
# Free Software Foundation; either version 3 of the License, or (at your
# option) any later version.
#
# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General
# Public License for more details.
#
# You should have received a copy of the GNU General Public License along
# with this program; if not, write to the Free Software Foundation, Inc.,
# 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA.


#
# =============================================================================
#
#                                   Preamble
#
# =============================================================================
#
"""
This modules provides access to all available distributions and functions for
reading distributions.
"""

from pycbc.distributions import from_file
from pycbc.distributions import gaussian
from pycbc.distributions import uniform

# dict of all distributions
distribs = {
    uniform.Uniform.name : uniform.Uniform,
    uniform.UniformAngle.name : uniform.UniformAngle,
    uniform.CosAngle.name : uniform.CosAngle,
    uniform.SinAngle.name : uniform.SinAngle,
    uniform.UniformSolidAngle.name : uniform.UniformSolidAngle,
    uniform.UniformSky.name : uniform.UniformSky,
    gaussian.Gaussian.name : gaussian.Gaussian,
    from_file.FromFile.name : from_file.FromFile,
}

def read_distributions_from_config(cp, section="prior"):
    """Returns a list of PyCBC distribution instances for a section in the
    given configuration file.

    Parameters
    ----------
    cp : WorflowConfigParser
        An open config file to read.
    section : {"prior", string}
        Prefix on section names from which to retrieve the distributions.

    Returns
    -------
    list
        A list of the parsed distributions.
    """
    dists = []
    variable_args = []
    for subsection in cp.get_subsections(section):
        name = cp.get_opt_tag(section, "name", subsection)
        dist = distribs[name].from_config(cp, section, subsection)
        if set(dist.params).isdisjoint(variable_args):
            dists.append(dist)
            variable_args += dist.params
        else:
            raise ValueError("Same parameter in more than one distribution.")
    return dists
