import atexit
import moderngl
import numpy as np
import os
import pyaudio
import pyrr
import threading
import time
from functools import partial
from matplotlib import cm
from PyQt5.QtCore import Qt, QBasicTimer, QTimer, QUrl
from PyQt5.QtGui import QIcon, QImage, QPixmap, QSurfaceFormat
from PyQt5.QtMultimedia import QMediaContent, QMediaPlayer, QAudioRecorder, QAudioEncoderSettings, QMultimedia
from PyQt5.QtWidgets import QApplication, QWidget, QGridLayout, QStackedWidget, QLabel, QVBoxLayout, QHBoxLayout, QOpenGLWidget
from scipy.fftpack import rfft, rfftfreq
from scipy.io import wavfile
#x = rfftfreq(WINDOW_SIZE, 1 / sample_rate)






WINDOW_SIZE      = 1024
HOP_SIZE         = 256
NTH_BIN          = 4
SAMPLE_RATE      = 22050

TEXTURE_WIDTH    = 1024
TEXTURE_HEIGHT   = WINDOW_SIZE // NTH_BIN

TIME_UNIT_WIDTH  = SAMPLE_RATE / HOP_SIZE
FREQ_UNIT_HEIGHT = TEXTURE_HEIGHT / (SAMPLE_RATE / 2) * 1000

AXIS_WIDTH       = 64
AXIS_HEIGHT      = 26








class Spectrogram:

	MAX_LOG = 16.0 # Max 16 is a design choice and not based on anything

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
		clipped = np.clip(log, 0, self.MAX_LOG)
		normalized = clipped / self.MAX_LOG
		strip = self.color_map(normalized)[:,:3]
		strip = (strip * 255).astype(np.uint8)
		return strip









class Source:

	def __init__(self, *args, **kwargs):
		self.data = None
		self.rate = 22050
		self.index = 0
		self.chunksize = 1024
		self.lock = threading.Lock()
		self.frames = []
		self.audio = pyaudio.PyAudio()
		self.stream = None
		atexit.register(self.close)
		self.init(*args, **kwargs)
		if not self.stream:
			raise Exception('self.stream is None')

	def init(self, *args, **kwargs):
		# Must implement to create stream object
		raise NotImplementedError('Source.init') 

	def callback(self, data, frame_count, time_info, status):
		# Designed to use PyAudio in callbackmode
		raise NotImplementedError('Source.callback') 

	def get_frames(self):
		with self.lock:
			frames = self.frames
			self.frames = []
			return frames

	def start(self):
		self.stream.start_stream()
	
	def stop(self):
		self.stream.stop_stream()

	def close(self):
		self.stream.close()
		self.audio.terminate()











class Microphone(Source):
	
	def init(self):
		self.stream = self.audio.open(
			format=pyaudio.paInt16,
			channels=1,
			rate=self.rate,
			input=True,
			frames_per_buffer=self.chunksize,
			stream_callback=self.callback)

	def callback(self, data, frame_count, time_info, status):
		data = np.frombuffer(data, dtype=np.int16)
		with self.lock:
			self.frames.append(data)
		return None, pyaudio.paContinue







class File(Source):

	def init(self, filename='audio/gettysburg.wav'):
		self.rate, self.data = wavfile.read(filename)
		self.stream = self.audio.open(
			format=pyaudio.paInt16,
			channels=1,
			rate=self.rate,
			output=True,
			stream_callback=self.callback)
		
	def callback(self, in_data, frame_count, time_info, status):
		data = self.data[self.index:self.index + self.chunksize]
		self.index += self.chunksize
		with self.lock:
			self.frames.append(data)
		return (data, pyaudio.paContinue)






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










class Surface(QOpenGLWidget):

	def __init__(self, width, height):
		super().__init__()
		# Set GL Version 3.3 core
		fmt = QSurfaceFormat()
		fmt.setVersion(3, 3)
		fmt.setProfile(QSurfaceFormat.CoreProfile)
		fmt.setDefaultFormat(fmt)
		fmt.setSamples(4)
		self.setFormat(fmt)
		self.width = width
		self.height = height
		self.setFixedSize(width, height)

	def initializeGL(self):
		# Vertex shader
		vertex = '''
			#version 330 core
			uniform mat4 orth;
			in vec4 vertex;
			out vec2 v_uv;
			void main() {
				gl_Position = orth * vec4(vertex.xy, 0.0, 1.0);
				v_uv = vertex.zw;
			}
		'''
		# Fragment shader
		fragment = '''
			#version 330 core
			uniform sampler2D image;
			in vec2 v_uv;
			out vec4 f_color;
			void main() {
				vec4 color = texture(image, v_uv);
				f_color = vec4(color.rgb, 1);
			}
		'''
		# Create otho projection matrix
		P = pyrr.Matrix44.orthogonal_projection(
				0, self.width, 0, self.height, 1, -1).astype('f4')
		# Create vertex data
		vertices = np.array([
			0,          0,           0.0, 1.0,
			self.width, 0,           1.0, 1.0,
			self.width, self.height, 1.0, 0.0,
			0,          0,           0.0, 1.0,
			self.width, self.height, 1.0, 0.0,
			0,          self.height, 0.0, 0.0
		])
		# Create GL context
		self.ctx = moderngl.create_context(require=330)
		# Set background color
		self.ctx.clear(0.0, 0.0, 0.0)
		# Needed for antialiasing
		self.ctx.multisample = True
		# Create Shader Program
		self.prog = self.ctx.program(vertex_shader=vertex, fragment_shader=fragment)
		self.prog['orth'].write(P)
		self.prog['image'].value = 0
		# Vertex Buffer Aray
		self.vbo = self.ctx.buffer(vertices.astype('f4').tobytes())
		# Vertex Attribute Array
		self.vao = self.ctx.vertex_array(self.prog, self.vbo, 'vertex')
		# Texture
		frame = (np.random.random((self.height, self.width, 3)) * 255).astype(np.uint8)
		self.set_texture(frame)

	def set_texture(self, frame):
		self.texture = self.ctx.texture(frame.shape[1::-1], frame.shape[2], frame)
		self.texture.repeat_x = False
		self.texture.repeat_y = False
		self.texture.use(0)
		self.update()

	def paintGL(self):
		self.texture.use(0)
		self.vao.render()

	def keyPressEvent(self, event):
		if event.key() == Qt.Key_Escape:
			self.close()












class Main(QWidget):

	def __init__(self):
		super().__init__()
		self.init_layout()
		self.spectrogram = Spectrogram()
		self.texture = np.zeros((TEXTURE_HEIGHT, TEXTURE_WIDTH, 3), dtype=np.uint8)
		
		self.buffer = Buffer()

		#self.source = Microphone()
		self.source = File()
		
		self._timer = QBasicTimer()
		self._timer.start(1000 // 31, self)

	def timerEvent(self, event):
		frames = self.source.get_frames()
		for frame in frames:
			self.buffer.add(frame)
		# Add new strips to texture
		count = 0
		while self.buffer.available():
			frame = self.buffer.get()
			self.update_texture(frame)
			count += 1
			if count == 3:
				break
		# Redraw spectrogram
		self.redraw_texture()

	def update_texture(self, window):
		self.texture[:, :-1] = self.texture[:, 1:]
		strip = self.spectrogram.get(window)
		self.texture[:, -1, :] = strip

	def redraw_texture(self):
		self.image.set_texture(self.texture.copy())

	def init_layout(self):
		# Load styles
		self.setStyleSheet('background-color: #141414')
		
		text_styles = '''
			color: #606265;
			font-family: mono;
			font-size: 10px;
			font-weight: bold;
		'''
		# Create spectrogram gl surface
		self.image = Surface(TEXTURE_WIDTH, TEXTURE_HEIGHT)

		self.setFixedSize(TEXTURE_WIDTH+AXIS_WIDTH, TEXTURE_HEIGHT+AXIS_HEIGHT)
		
		time_axis = QWidget()
		time_axis.setFixedHeight(AXIS_HEIGHT)
		# Add all ticks and labels to time axis
		for i in range(int(TEXTURE_WIDTH // TIME_UNIT_WIDTH) + 1):
			x = int(TEXTURE_WIDTH - (i+1) * TIME_UNIT_WIDTH)
			
			n_ticks = 10
			for j in range(n_ticks):
				tick = QWidget(time_axis)
				tick.setStyleSheet(f'background-color: #2a2a2f')
				tick.setGeometry(x + int(TIME_UNIT_WIDTH / n_ticks * j), 0, 1, 4)
			# Add ticks
			tick = QWidget(time_axis)
			tick.setStyleSheet('background-color: #4a4a4f;')
			tick.setGeometry(x, 0, 1, 6)
			# Only display every nth integer seconds on time axis
			n = 2
			if i % n == 0 or x <= 0:
				continue
			# Add seconds text
			time = QLabel(f'-{i+1}s', time_axis)
			time.setStyleSheet(text_styles)
			time.setGeometry(x-20, 10, 40, 10)
			time.setAlignment(Qt.AlignCenter | Qt.AlignVCenter)
		
		freq_axis = QWidget()
		freq_axis.setFixedWidth(AXIS_WIDTH)
		# Add all ticks and labels to frequency axis
		for i in range(int(TEXTURE_HEIGHT // FREQ_UNIT_HEIGHT)):
			y = int(TEXTURE_HEIGHT - (i+0) * FREQ_UNIT_HEIGHT)
			# Dont display odd i values, [0, 2, 4, 6, ...]
			if i % 2 != 0:
				continue
			# Add ticks
			tick = QWidget(freq_axis)
			tick.setStyleSheet('background-color: #4a4a4f;')
			tick.setGeometry(AXIS_WIDTH-6, y, 6, 1)
			# Add seconds text	
			freq = QLabel(f'{i*1000}hz', freq_axis)
			freq.setStyleSheet(text_styles)
			freq.setGeometry(0, y-5, AXIS_WIDTH-12, 10)
			freq.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
		
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
	#main = Surface(1024, 512)
	main = Main()
	main.show()
	
	# Run main loop
	app.exit(app.exec())







