import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker

data = np.random.rand(88, 1440)

interval = 1  # minutes
extent = [0, data.shape[1]*interval, 0, data.shape[0]]

plt.imshow(data, extent=extent, aspect='auto', origin='lower',
           cmap='gray_r', vmin=0, vmax=1)

# Format the seconds on the axis as min:sec
def fmtsec(x,pos):
    return "{:02d}:{:02d}".format(int(x//60), int(x%60))
plt.gca().xaxis.set_major_formatter(mticker.FuncFormatter(fmtsec))
# Use nice tick positions as multiples of 30 seconds
plt.gca().xaxis.set_major_locator(mticker.MultipleLocator(120))

plt.xlabel('Time')
plt.colorbar()
plt.show()
