import numpy as np
import os
import pyaudio
import time
from functools import partial
from matplotlib import cm
from PyQt5.QtCore import Qt, QBasicTimer, QTimer, QUrl
from PyQt5.QtGui import QIcon, QImage, QPixmap
from PyQt5.QtMultimedia import QMediaContent, QMediaPlayer
from PyQt5.QtWidgets import QApplication, QWidget, QGridLayout, QStackedWidget, QLabel, QVBoxLayout, QHBoxLayout
from scipy.fftpack import rfft, rfftfreq
from scipy.io import wavfile



SECONDS_WIDTH = 180

WINDOW_SIZE = 512
HOP_SIZE = 256
NTH_BIN = 2
MAX_LOG = 16.0

SPEC_WIDTH = 1024
SPEC_HEIGHT = WINDOW_SIZE // NTH_BIN

color_map = cm.get_cmap('inferno', 256)



def hann_window(k):
	return 0.5 * (1 - np.cos((2 * np.pi * np.arange(1, k+1)) / (k-1)))

# Create hann window up front
hann = hann_window(WINDOW_SIZE)


sample_rate, data = wavfile.read('gettysburg.wav')




def calc_strip(window):
	tapered = window * hann
	transform = rfft(tapered)
	magnitude = np.abs(transform)[::-NTH_BIN]
	log = np.log(magnitude)
	clipped = np.clip(log, 0, MAX_LOG) # Max 16 is a design choice and not based on anything
	normalized = clipped / MAX_LOG
	return normalized



#x = rfftfreq(WINDOW_SIZE, 1 / sample_rate)
#print(x.min(), x.max())



class Main(QWidget):

	def __init__(self):
		super().__init__()
		
		self.init_layout()
		
		self.texture = np.zeros((256, SPEC_WIDTH, 3), dtype=np.uint8)
		self.update_texture()
		
		self.index = 0
		
		filename = os.path.join(os.getcwd(), 'gettysburg.wav')

		media = QMediaContent(QUrl.fromLocalFile(filename))
		
		self.player = QMediaPlayer()
		self.player.mediaStatusChanged.connect(self.on_media_status)
		self.player.positionChanged.connect(self.on_position)
		self.player.durationChanged.connect(self.on_duration)
		self.player.setMedia(media)
		self.player.play()

		self._timer = QBasicTimer()
		self._timer.start(1000 // 60, self)
		
		#self.timer = QTimer()
		#self.timer.timeout.connect(self.update_timer)
		#self.timer.setInterval(1000 / 33)
		#self.timer.start(1000 // 60, self)

	
	def on_media_status(self, status):
		print('status', status)
		#if status == QMediaPlayer.EndOfMedia:
	#		self.on_end()

	def on_position(self, position):
		pass

	def on_duration(self, duration):
		print('duration', duration / 1000)
		#self.slider.setRange(0, duration)
		#s = duration // 1000
		#m = 0
		#h = 0
		#if s >= 60:
	#		m = s // 60
	#		s = s % 60
#		if m >= 60:
#			h = m // 60
#			m = m % 60
#		text = f'{"0" if m < 10 else ""}{m}:{"0" if s < 10 else ""}{s}'
#		if h > 0:
#			text = f'{h}:{text}'
#		self.duration.setText(text)
	
	def next_window(self):
		#texture = self.texture.copy()
		self.texture[:, :-1] = self.texture[:, 1:]
		
		window = data[self.index*HOP_SIZE:self.index*HOP_SIZE + WINDOW_SIZE]
		if window.size != 512:
			return
		
		strip = calc_strip(window)
		strip = color_map(strip)[:,:3]
		strip = (strip * 255).astype(np.uint8)
		self.texture[:, -1, :] = strip
		
		self.index += 1


	def update_texture(self, spec=None):
		h, w, c = self.texture.shape
		new_image = QImage(self.texture.data, w, h, c*w, QImage.Format_RGB888)
		self.image.setPixmap(QPixmap(new_image))


	def timerEvent(self, event):
		seconds = self.player.position() / 1000
		while (self.index * HOP_SIZE + WINDOW_SIZE) / sample_rate < seconds + 0.0:
			self.next_window()
		
		self.update_texture()


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
		
		self.image = QLabel()
		
		time_axis = QWidget()
		time_axis.setFixedHeight(AXIS_HEIGHT)
		
		# Add all ticks and labels to time axis
		for i in range(SPEC_WIDTH // SECONDS_WIDTH + 1):
			x = SPEC_WIDTH - (i+1) * SECONDS_WIDTH
			# Add ticks
			n_ticks = 20
			for j in range(n_ticks):
				if j in [1, 2, 3]:
					continue
				tick = QWidget(time_axis)
				tick.setStyleSheet(f'background-color: {"#4a4a4f" if j == 0 else "#25252c"};')
				tick.setGeometry(x + int(SECONDS_WIDTH / n_ticks * j), 6, 1, AXIS_HEIGHT-11)
			# Add seconds text	
			time = QLabel(f'-{i+1}s', time_axis)
			time.setStyleSheet(text_styles)
			time.move(x+8, 6)
		
		freq_axis = QWidget()
		freq_axis.setFixedWidth(AXIS_WIDTH)
		
		# Add all ticks and labels to frequency axis
		for freq in [0, 2500, 5000, 7500, 10000]:
			y = int(SPEC_HEIGHT - (freq / (sample_rate / 2)) * SPEC_HEIGHT)
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







