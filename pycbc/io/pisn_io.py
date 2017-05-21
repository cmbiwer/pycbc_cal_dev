import numpy
import pickle

def read_pisn_files(input_files, min_snr=None, max_snr=None):
    min_snr = min_snr if min_snr else 0.0
    max_snr = max_snr if max_snr else numpy.inf
    injecteds = []
    intervals = []
    total = len(input_files)
    for i, input_file in enumerate(input_files):
        intervals_from_file, injecteds_from_file = pickle.load(open(input_file, "r"))
        print input_file, "has", len(injecteds_from_file), "signals"
        for interval, injected in zip(intervals_from_file, injecteds_from_file):
            if interval["snr_med"] > min_snr and interval["snr_med"] < max_snr:
                injecteds.append(injected)
                intervals.append(interval)
        print "checked", i + 1, "of", total, "files"
    return intervals, injecteds

