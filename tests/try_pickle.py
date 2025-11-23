#!/usr/bin/env python3

import pickle

class MyUnpickler(pickle.Unpickler):
    def persistent_load(self, pid):
        print("Resolving persistent id:", pid)
        # Decide how to handle it
        return None  # or return a real object

with open('models/data.pkl', 'rb') as pkl_fobj:

    # Dangerous
    obj = MyUnpickler(pkl_fobj).load()
    #obj = pickle.loads(pkl_fobj.read())


import torch

obj = torch.load("models/data.pkl", map_location="cpu")

breakpoint()