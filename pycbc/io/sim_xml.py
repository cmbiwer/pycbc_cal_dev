# Copyright (C) 2017 Christopher M. Biwer
# This program is free software; you can redistribute it and/or modify it
# under the terms of the GNU General Public License as published by the
# Free Software Foundation; either version 3 of the License, or (at your
# self.option) any later version.
#
# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General
# Public License for more details.
#
# You should have received a copy of the GNU General Public License along
# with this program; if not, write to the Free Software Foundation, Inc.,
# 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA.
""" This modules defines functions for handling SimInspiral objects.
"""

import glue
from glue.ligolw import ilwd
from glue.ligolw import ligolw
from glue.ligolw import lsctables
from glue.ligolw import utils
import logging
from pycbc import detector
from pycbc.types import optparse
import sys

def empty_sim_inspiral(i):
    """ Return empty SimInspiral.

    Returns
    --------
    lsctables.SimInspiral
        The "empty" SimInspiral object.
    """
    sim = lsctables.SimInspiral()
    cols = lsctables.SimInspiralTable.validcolumns
    for entry in cols.keys():
        if cols[entry] in ["real_4","real_8"]:
            setattr(sim,entry,0.)
        elif cols[entry] == "int_4s":
            setattr(sim,entry,0)
        elif cols[entry] == "lstring":
            setattr(sim,entry,"")
        elif entry == "process_id":
            sim.process_id = ilwd.ilwdchar("process:process_id:0")
        elif entry == "simulation_id":
            sim.simulation_id = ilwd.ilwdchar(
                                           "sim_inspiral:simulation_id:%d" % i)
        else:
            raise ValueError("Column %s not recognized" %(entry) )
    return sim

def empty_ligolw_document(opts):
    """ Returns an empty LIGOLW XML document.
    """

    # create Document
    outdoc = ligolw.Document()
    outdoc.appendChild(ligolw.LIGO_LW())

    # put opts into a dict for the process table
    opts_dict = optparse.convert_to_process_params_dict(opts)

    # create process table
    proc_id = utils.process.register_to_xmldoc(
                        outdoc, sys.argv[0], opts_dict,
                        comment="", ifos=["".join(opts.instruments)],
                        version=glue.git_version.id,
                        cvs_repository=glue.git_version.branch,
                        cvs_entry_time=glue.git_version.date).process_id

    return outdoc

def parse_to_column(sim, key, value):

    # if distribution parameter matches column name then use it
    if hasattr(sim, key):
        setattr(sim, key, value)

    # set coalescence time into integer and nanosecond integer columns
    elif key == "tc":
        sim.geocent_end_time = int(value)
        sim.geocent_end_time_ns = int(value % 1 * 1e9)

    # set sky position into longitude and latitude columns
    elif key == "ra":
        sim.longitude = value
    elif key == "dec":
        sim.latitude = value

    # otherwise do not know what to do with this parameter
    else:
        logging.info("Ignored %s", key)

def ifo_time_to_column(sim, ifo, end_time):
    """ Saves the specific IFO time column.
    """
    setattr(sim, ifo[0].lower() + "_end_time", int(end_time))
    setattr(sim, ifo[0].lower() + "_end_time_ns", int(end_time % 1 * 1e9))

def ifo_distance_to_column(sim, ifo, f_plus, f_cross):
    """ Saves the specific IFO effective distance column,
    """
    eff_distance = detector.effective_distance(sim.distance, sim.inclination,
                                               f_plus, f_cross)
    setattr(sim, "eff_dist_" + ifo[0].lower(), eff_distance)

