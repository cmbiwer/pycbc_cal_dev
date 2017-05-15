import pickle

def read_pisn_files(input_files):
    injected = []
    intervals = []
    total = len(input_files)
    for i, input_file in enumerate(input_files):
        interval_i, injected_i =  pickle.load(open(input_file, "r"))
        injected += injected_i
        intervals += interval_i
        print "loaded", i + 1, "of", total, "files"
    return intervals, injected

