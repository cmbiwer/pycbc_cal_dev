#! /usr/bin/python

import ROOT
ROOT.gSystem.Load("/usr/lib64/libdmtsigp.so")
ROOT.gSystem.Load("/usr/lib64/libgdsplot.so")
from foton import FilterFile

# read the foton filter file
filter_file = FilterFile('L1OAF.txt')
