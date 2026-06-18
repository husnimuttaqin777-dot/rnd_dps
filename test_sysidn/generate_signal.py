import pandas as pd
import numpy as np

K = 1.5
tau = 2.0

t = np.arange(100) * 10
y = K * (1 - np.exp(-t / tau))

df = pd.DataFrame({
    "x": t,
    "y": y
})

df.to_csv("signal1.csv", index=False)