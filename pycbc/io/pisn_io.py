import pickle

def read_pisn_files(input_files):
    injected = []
    intervals = []
    for input_file in input_files:
        interval_i, injected_i =  pickle.load(open(input_file, "r"))
        injected += injected_i
        intervals += interval_i
    return intervals, injected

