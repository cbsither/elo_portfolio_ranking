import numpy as np

def generate_returns(arr):
    return np.diff(arr, axis=1) / arr[:, :-1]