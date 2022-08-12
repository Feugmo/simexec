# In[1]:

import copy
import json
import math

import GPyOpt
import numpy as np
import pandas as pd
from plotly.offline import download_plotlyjs, init_notebook_mode, plot
from pymatgen.core import Composition

raw_dataset = pd.read_csv(r"res.csv")

# In[2]:
print(raw_dataset.head())

# In[3]:
element_list = ["Mg", "Al"]
X_feature = []
for i in range(len(raw_dataset)):
    comp = Composition(raw_dataset["name"][i])
    X_feature.append(np.array([comp.get_wt_fraction(elm) for elm in element_list]))
X_feature = np.vstack(X_feature)

print(X_feature.shape)

# In[4]:
dataset = copy.deepcopy(raw_dataset)

dataset["Mg"] = X_feature[:, 0]
dataset["Al"] = X_feature[:, 1]

dataset = dataset[["MP ID", "Mg", "Al", "energy"]]

print(dataset.head())

dataset.to_csv("MgAl.csv", index=False)
