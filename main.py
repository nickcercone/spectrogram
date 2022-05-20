import atexit
import numpy as np
import os
import pyaudio
import threading
import time
from functools import partial
from matplotlib import cm
from PyQt5.QtCore import Qt, QBasicTimer, QTimer, QUrl
from PyQt5.QtGui import QIcon, QImage, QPixmap
from PyQt5.QtMultimedia import QMediaContent, QMediaPlayer, QAudioRecorder, QAudioEncoderSettings, QMultimedia
from PyQt5.QtWidgets import QApplication, QWidget, QGridLayout, QStackedWidget, QLabel, QVBoxLayout, QHBoxLayout
from scipy.fftpack import rfft, rfftfreq
from scipy.io import wavfile


from graphics import Surface





WINDOW_SIZE = 1024
HOP_SIZE    = 256
NTH_BIN     = 4
SAMPLE_RATE = 22050





#x = rfftfreq(WINDOW_SIZE, 1 / sample_rate)




class Spectrogram:

	MAX_LOG = 16.0

	def __init__(self, theme='inferno'):
		self.color_map = cm.get_cmap(theme, 256)
		self.hann = self.hann_window(WINDOW_SIZE)
		
	def hann_window(self, k):
		return 0.5 * (1 - np.cos((2 * np.pi * np.arange(1, k+1)) / (k-1)))
	
	def get(self, window):
		tapered = window * self.hann
		transform = rfft(tapered)
		magnitude = np.abs(transform)[::-NTH_BIN]
		log = np.log(magnitude)
		clipped = np.clip(log, 0, self.MAX_LOG) # Max 16 is a design choice and not based on anything
		normalized = clipped / self.MAX_LOG
		strip = self.color_map(normalized)[:,:3]
		strip = (strip * 255).astype(np.uint8)
		return strip






class Microphone:
	
	def __init__(self, rate=22050, chunksize=1024):
		self.rate = rate
		self.chunksize = chunksize
		self.lock = threading.Lock()
		self.stop = False
		self.frames = []
		self.audio = pyaudio.PyAudio()
		self.stream = self.audio.open(
			format=pyaudio.paInt16,
			channels=1,
			rate=self.rate,
			input=True,
			frames_per_buffer=self.chunksize,
			stream_callback=self.callback)
		atexit.register(self.close)

	def callback(self, data, frame_count, time_info, status):
		data = np.frombuffer(data, dtype=np.int16)
		with self.lock:
			self.frames.append(data)
			if self.stop:
				return None, pyaudio.paComplete
		return None, pyaudio.paContinue

	def get_frames(self):
		with self.lock:
			frames = self.frames
			self.frames = []
			return frames

	def start(self):
		self.stream.start_stream()

	def close(self):
		with self.lock:
			self.stop = True
		self.stream.close()
		self.audio.terminate()







class File:
	
	def __init__(self, filename='audio/gettysburg.wav', chunksize=1024):
		self.rate, self.data = wavfile.read(filename)
		self.chunksize = chunksize
		self.index = 0
		self.lock = threading.Lock()
		self.stop = False
		self.frames = []
		self.audio = pyaudio.PyAudio()
		self.stream = self.audio.open(
			format=pyaudio.paInt16,
			channels=1,
			rate=self.rate,
			output=True,
			stream_callback=self.callback)
		atexit.register(self.close)
		
	def callback(self, in_data, frame_count, time_info, status):
		data = self.data[self.index:self.index + self.chunksize]
		self.index += self.chunksize
		with self.lock:
			self.frames.append(data)
		return (data, pyaudio.paContinue)

	def get_frames(self):
		with self.lock:
			frames = self.frames
			self.frames = []
			return frames

	def start(self):
		self.stream.start_stream()

	def close(self):
		with self.lock:
			self.stop = True
		self.stream.close()
		self.audio.terminate()







class Buffer:

	def __init__(self):
		self.data = []
		self.index = 0

	def add(self, buf):
		self.data += buf.tolist()
	
	def available(self):
		if self.index + WINDOW_SIZE <= len(self.data):
			return True
		return False

	def get(self):
		frame = self.data[self.index:self.index + WINDOW_SIZE]
		self.index += HOP_SIZE
		return frame








class Main(QWidget):

	TIME_UNIT_WIDTH = 180
	TEXTURE_WIDTH = 1024
	TEXTURE_HEIGHT = WINDOW_SIZE // NTH_BIN
	
	def __init__(self):
		super().__init__()
		self.init_layout()
		self.spectrogram = Spectrogram()
		self.texture = np.zeros((self.TEXTURE_HEIGHT, self.TEXTURE_WIDTH, 3), dtype=np.uint8)
		#self.redraw_texture()
		self.buffer = Buffer()
		self.microphone = Microphone()
		#self.microphone.start()
		self.file = File()
		self.file.start()
		#self.source = 'microphone'
		self.source = 'file'
		self._timer = QBasicTimer()
		self._timer.start(1000 // 30, self)

	def timerEvent(self, event):
		if self.source == 'microphone':
			frames = self.microphone.get_frames()

		if self.source == 'file':
			frames = self.file.get_frames()
		
		for frame in frames:
			self.buffer.add(frame)
		# Add new strips to texture
		count = 0
		while self.buffer.available():
			frame = self.buffer.get()
			self.update_texture(frame)
			count += 1
		#	print(count)
			if count == 6:
				break
		# Redraw spectrogram
		self.redraw_texture()

	def update_texture(self, window):
		self.texture[:, :-1] = self.texture[:, 1:]
		strip = self.spectrogram.get(window)
		self.texture[:, -1, :] = strip

	def redraw_texture(self):
		#h, w, c = self.texture.shape
		#new_image = QImage(self.texture.data, w, h, c*w, QImage.Format_RGB888)
		#self.image.setPixmap(QPixmap(new_image))
		self.image.set_texture(self.texture.copy())
		#pass 

	def init_layout(self):
		# Load styles
		self.setStyleSheet('background-color: #141414')
		
		AXIS_WIDTH = 64
		AXIS_HEIGHT = 25
		
		text_styles = '''
			color: #70737b;
			font-family: mono;
			font-size: 10px;
			font-weight: bold;
		'''
#		self.image = QLabel()
		self.image = Surface()
		self.image.setFixedSize(1024, 256)
		
		time_axis = QWidget()
		time_axis.setFixedHeight(AXIS_HEIGHT)
		# Add all ticks and labels to time axis
		for i in range(self.TEXTURE_WIDTH // self.TIME_UNIT_WIDTH + 1):
			x = self.TEXTURE_WIDTH - (i+1) * self.TIME_UNIT_WIDTH
			# Add ticks
			n_ticks = 20
			for j in range(n_ticks):
				if j in [1, 2, 3]:
					continue
				tick = QWidget(time_axis)
				tick.setStyleSheet(f'background-color: {"#4a4a4f" if j == 0 else "#25252c"};')
				tick.setGeometry(x + int(self.TIME_UNIT_WIDTH / n_ticks * j), 6, 1, AXIS_HEIGHT-11)
			# Add seconds text	
			time = QLabel(f'-{i+1}s', time_axis)
			time.setStyleSheet(text_styles)
			time.move(x+8, 6)
		
		freq_axis = QWidget()
		freq_axis.setFixedWidth(AXIS_WIDTH)
		# Add all ticks and labels to frequency axis
		for freq in [0, 2500, 5000, 7500, 10000]:
			y = int(self.TEXTURE_HEIGHT - (freq / (SAMPLE_RATE / 2)) * self.TEXTURE_HEIGHT)
			# Add ticks
			tick = QWidget(freq_axis)
			tick.setStyleSheet('background-color: #4a4a4f;')
			tick.setGeometry(AXIS_WIDTH-7, y, 4, 1)
			# Add seconds text	
			time = QLabel(f'{freq}hz', freq_axis)
			time.setStyleSheet(text_styles)
			time.setGeometry(0, y-5, AXIS_WIDTH-12, 10)
			time.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
		
		image_time_parent = QWidget()
		
		v_box = QVBoxLayout(image_time_parent)
		v_box.setContentsMargins(0,0,0,0)
		v_box.setSpacing(0)
		v_box.addWidget(self.image)
		v_box.addWidget(time_axis)
		
		h_box = QHBoxLayout(self)
		h_box.setContentsMargins(0,0,0,0)
		h_box.setSpacing(0)
		h_box.addWidget(freq_axis)
		h_box.addWidget(image_time_parent)


	def keyPressEvent(self, event):
		if event.key() == Qt.Key_Escape:
			self.close()








if __name__ == '__main__':
	
	# Correctly scale on high res monitors
	QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)

	# Use highdpi icons
	QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps, True)
	
	# Create and run glwidget
	app = QApplication([])

	# Create window
	main = Main()
	main.show()
	
	# Run main loop
	app.exit(app.exec())







