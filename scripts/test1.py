import torch
import numpy as np
import pandas as pd
import scipy
import matplotlib
import pyvinecopulib as pv

print("torch:", torch.__version__)
print("CUDA available:", torch.cuda.is_available())
print("GPU:", torch.cuda.get_device_name(0) if torch.cuda.is_available() else "None")
print("numpy:", np.__version__)
print("pandas:", pd.__version__)
print("scipy:", scipy.__version__)
print("matplotlib:", matplotlib.__version__)
print("pyvinecopulib:", pv.__version__)