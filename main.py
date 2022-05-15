#import librosa
#import librosa.display
import math
import matplotlib.pyplot as plt
import numpy as np
import time
from scipy.fftpack import rfft, rfftfreq
from scipy.io import wavfile

import matplotlib
matplotlib.use('QtAgg')


WINDOW_SIZE = 512
HOP_SIZE = 128


def hann_window(k):
	return 0.5 * (1 - np.cos((2 * np.pi * np.arange(1, k+1)) / (k-1)))

# Create hann window up front
hann = hann_window(WINDOW_SIZE)

sample_rate, data = wavfile.read('imperial-march.wav')
#sample_rate, data = wavfile.read('gettysburg.wav')

data = data[data.size // 2:]

print(data[:10])

#data, sample_rate = librosa.load('gettysburg.wav')


print(data[:10])



#print(sample_rate)
#X = librosa.stft(data)
#print(X.shape)
#Xdb = librosa.amplitude_to_db(abs(X))
#plt.figure(figsize=(14, 5))
#librosa.display.specshow(Xdb, sr=sample_rate, x_axis='time', y_axis='hz')
#plt.colorbar()
#plt.show()

# Total frames for 
n_frames = int((data.size - WINDOW_SIZE) / HOP_SIZE) + 1


frame  = np.zeros((WINDOW_SIZE, n_frames))


for i in range(n_frames):

	window = data[i*HOP_SIZE:i*HOP_SIZE + WINDOW_SIZE]
	
	tapered = window * hann
	
	transform = rfft(tapered)

	magnitude = np.abs(transform)
	
	log = np.log(magnitude)
	
	clipped = np.clip(log, 0, 15) # Max 15 is a design choice and not based on anything
	
	normalized = clipped / 15.0 

	frame[:, i] = normalized[::-1]


plt.imshow(frame, cmap='inferno')
plt.colorbar()
plt.show()







#dB = 20 * np.log10(magnitude)
#dB = librosa.amplitude_to_db(magnitude)




#print('Total samples:', data.size, ' duration:', data.size / sample_rate)

#plt.plot(data[:WINDOW_SIZE])
#plt.xlabel('Sample Index')
#plt.ylabel('Amplitude')
#plt.show()





#hann = hann_window(WINDOW_SIZE)

#plt.plot(hann)
#plt.show()




#tapered = data[:WINDOW_SIZE] * hann

#plt.plot(tapered)
#plt.xlabel('Sample Index')
#plt.ylabel('Amplitude')
#plt.show()





#x = rfftfreq(WINDOW_SIZE, 1 / sample_rate)
#y = rfft(tapered)
#y = np.abs(y)

#print(x.size, y.size)


#plt.plot(x, y)
#plt.xlabel('Frequency')
#plt.ylabel('Amplitude')
#plt.ticklabel_format(style='plain')
#plt.show()












#BINS_PER_SECOND = 32





#start = time.time()





# def fft_for_segment(i, dt=0.1):
#	h = sample_rate * dt
#	a = int( i    * h)
#	b = int((i+1) * h)
#	sample = data[a:b]
#	x = rfftfreq(b-a, 1 / sample_rate)
#	y = rfft(sample)
#	y = np.abs(y)
#	return x, y





# def binify(arr, n_bins):
#	'''
#	Take a 1D numpy array of any length and break it up into n bins. If the
#	data does not fit neatly into n bins and contains a remainder, just throw
#	that extra little bit away.
#	'''
#	total = arr.shape[0]
#	remainder = total % n_bins
#	# Trim from the end of the buffer if needed so that we can reshape evenly
#	if remainder > 0:
#		print(remainder)
#		arr = arr[:-remainder]
#		total = arr.shape[0]
#	
#	return arr.reshape(n_bins, -1)





# def equalish_bins(array, n):
#	bins = []
#	for i in range(n):
#		a = int(( i    / n) * array.size)
#		b = int(((i+1) / n) * array.size)
#		bins.append(array[a:b])
#	return bins


# def anchor_point(i, sample_rate):
#	return int((i / BINS_PER_SECOND) * sample_rate) 


# Bin audio samples into exactly BINS_PER_SECOND for every sample_rate samples

#time_bins = []

#n_time_bins = math.ceil(data.size / (sample_rate / BINS_PER_SECOND))


#for i in range(n_time_bins):
#	a = anchor_point(i,   sample_rate)
#	b = anchor_point(i+1, sample_rate)
#	time_bin = data[a:b]
#	time_bins.append(time_bin)


# Fast Discrete Fourier Transform each time bin

#transform_bins = []

#for time_bin in time_bins:
#	x = rfftfreq(time_bin.size, 1 / sample_rate)
#	y = rfft(time_bin)
#	y = np.abs(y)
#	transform_bins.append([x, y])

#x, y = transform_bins[0]

#print(x.size, y.size)


#plt.plot(x, y)
#plt.xlabel('Frequency')
#plt.ylabel('Amplitude')
#plt.ticklabel_format(style='plain')
#plt.show()


#pixel_w = len(transform_bins)
#pixel_h = 256*2

#frame = np.zeros((pixel_h, pixel_w*2))

#for wi in range(pixel_w):
#	_, y = transform_bins[wi]
#
#	bins = equalish_bins(y, pixel_h)
#
#	for hi in range(pixel_h):
#		frame[pixel_h-hi-1, wi*2:(wi+1)*2] = np.log(bins[hi].max())



#print(time.time()-start)



#plt.imshow(frame)
#plt.show()




































#total = int(np.ceil(data.shape[0] / (sample_rate * dt)))



#frame = np.zeros(256, total)



#for i in range(int(total)):
#	a = int( i    * sample_rate * dt)
#	b = int((i+1) * sample_rate * dt)
#	sample = data[a:b]
#	n = sample.shape[0]
#	x = rfftfreq(n, 1 / sample_rate)
#	y = rfft(sample)
#	y = np.abs(y)
#	print(x.shape, y.shape)
	


#sample_rate = 97

#indices = np.arange(sample_rate)

#print(indices)

#frame_rate = 10





#for i in range(frame_rate):

	#a =  i    / frame_rate
	#b = (i+1) / frame_rate
	#a = int(a * sample_rate)
	#b = int(b * sample_rate)
	#print(a, b)
#	print(indices[a:b])










#print(total, 176, total / 176)




#print(n)














#x, y = fft_for_segment(0, dt=1)

#print(x)
#print(y)

#plt.plot(data)
#plt.show()
#duration = data.shape[0] / sample_rate
#xf = rfftfreq(data.shape[0], 1 / sample_rate)
#yf = rfft(data)
#xf = xf[:5000]
#yf = yf[:5000]
#print('n', n)

#for i in range(10):

#	x, y = fft_for_segment(i, 0.1)
	#print(x.shape, y.shape)
#	print(x.shape, y.shape)
	
#	plt.plot(x, y)
#	plt.xlabel('Frequency')
#	plt.ylabel('Amplitude')
#	plt.ticklabel_format(style='plain')
#	plt.show()



#plt.plot(data)
#plt.show()


