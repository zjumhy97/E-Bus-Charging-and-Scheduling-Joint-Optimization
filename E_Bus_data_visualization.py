#!/usr/bin/env python3.7

# Copyright 2020, Haoyu Miao

# This Program is for the Joint optimization of the E-Bus Charging and Scheduling - Data Visualization

import pandas as pd
from pandas import DataFrame as df
from matplotlib import pyplot as plt
import time

#fig, ax = plt.subplots()
#df.plot.barh(stacked=True, ax=ax)
#ax.set_yticklabels(['A', 'B', 'C', 'D', 'E', 'F'])
#time = pd.date_range(start=pd.to_datetime('07:00', format='%H:%M'), end=pd.to_datetime('13:00', format='%H:%M'),freq='H')
#time_x = [dt.strftime('%H:%M') for dt in time]
#ax.set_xticklabels(time_x)
#fig.autofmt_xdate()
#plt.show()

speed = [0.1, 17.5, 40, 48, 52, 69, 88]
lifespan = [2, 8, 70, 1.5, 25, 12, 28]
index = ['snail', 'pig', 'elephant',
         'rabbit', 'giraffe', 'coyote', 'horse']
df = pd.DataFrame({'speed': speed,
                   'lifespan': lifespan}, index=index)
ax = df.plot.barh()
plt.show()

#index = E_Bus
#df = pd.DataFrame()
#ax = df.plot.barh()
#plt.show()







