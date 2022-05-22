import math
import matplotlib.pyplot as plt
import numpy as np
import time
from scipy.fftpack import rfft, rfftfreq
from scipy.io import wavfile
import matplotlib


matplotlib.use('QtAgg')


WINDOW_SIZE = 512
HOP_SIZE = 256
NTH_BIN = 1

# Used to clip the log of the amplitude and create upper bound to then
# noralize from [0,16] -> [0,1]
MAX_LOG = 16.0

#sample_rate, data = wavfile.read('imperial-march.wav')
sample_rate, data = wavfile.read('audio/gettysburg.wav')

n_frames = int((data.size - WINDOW_SIZE) / HOP_SIZE) + 1

frame  = np.zeros((WINDOW_SIZE // NTH_BIN, n_frames))


def hann_window(k):
	return 0.5 * (1 - np.cos((2 * np.pi * np.arange(1, k+1)) / (k-1)))

# Create hann window up front
hann = hann_window(WINDOW_SIZE)



def calc_strip(window):
	tapered = window * hann
	transform = rfft(tapered)
	magnitude = np.abs(transform)[::-NTH_BIN]
	log = np.log(magnitude)
	clipped = np.clip(log, 0, MAX_LOG) 
	normalized = clipped / MAX_LOG
	return normalized


for i in range(n_frames):
	window = data[i*HOP_SIZE:i*HOP_SIZE + WINDOW_SIZE]
	frame[:, i] = calc_strip(window)


plt.imshow(frame, cmap='inferno')
plt.colorbar()
plt.show()






