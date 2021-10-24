from numpy.random.mtrand import rand
import pandas as pd
from numpy import *
import matplotlib.pyplot as plt
ts = pd.Series(random.randn(1000), index=pd.date_range('1/1/2000',periods=1000))
ts = ts.cumsum()
ts.plot()
plt.show()