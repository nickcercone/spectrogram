import pyaudio
import time
from scipy.io import wavfile




sample_rate, data = wavfile.read('gettysburg.wav')
#sample_rate, data = wavfile.read('adventures.wav')



print(sample_rate)
print(type(data), data.dtype)



class AudioPlayer:

	def __init__(self):
		
		self.chunk = 0
		self.chunk_size = 1024#*10
		
		self.p = pyaudio.PyAudio()

#		exit()
	
		self.stream = self.p.open(
				format=pyaudio.paInt16,
				channels=1,
				rate=sample_rate,
				output=True,
				frames_per_buffer=self.chunk_size,
				stream_callback=self.callback
			)
		self.stream.start_stream()

		while self.stream.is_active():
			time.sleep(1)

	def callback(self, in_data, frame_count, time_info, status):
		
		print(frame_count, time_info, status)
		
		chunk = data[self.chunk:self.chunk + self.chunk_size]
		self.chunk += self.chunk_size
		#data = wf.readframes(frame_count)
		return (chunk, pyaudio.paContinue)


audio = AudioPlayer()


#time.sleep(5)




