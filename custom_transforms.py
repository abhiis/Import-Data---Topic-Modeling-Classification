import numpy as np
def pass_through(x):
    return x

def convert_to_string(x):
    # If x is a list or an array with one element, extract the element
    if isinstance(x, (list, np.ndarray)) and len(x) == 1:
        x = x[0]
    
    if isinstance(x, bytes):  # Directly handle bytes objects
        return x.decode('utf-8')
    else:  # Handle everything else as string
        return str(x)