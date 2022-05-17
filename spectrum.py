import numpy as np
import os
import time

from functools import partial
from matplotlib import cm
from PyQt5.QtCore import Qt, QBasicTimer
from PyQt5.QtGui import QIcon, QImage, QPixmap
from PyQt5.QtWidgets import QApplication, QWidget, QGridLayout, QStackedWidget, QLabel, QVBoxLayout, QHBoxLayout
from scipy.fftpack import rfft, rfftfreq
from scipy.io import wavfile


AXIS_WIDTH = 64
AXIS_HEIGHT = 25

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



x = rfftfreq(WINDOW_SIZE, 1 / sample_rate)

print(x.min(), x.max())



class Main(QWidget):

	def __init__(self):
		super().__init__()
#		self.setWindowTitle('Dribl Vision')
#		self.setWindowIcon(QIcon(icon_file))
#		self.setFixedSize(WINDOW_WIDTH + 100, WINDOW_HEIGHT + 100)
		self.init_layout()

		self.spec = np.zeros((256, SPEC_WIDTH, 3), dtype=np.uint8)
		self.update_spec(self.spec)
		
		self.index = 0

		self._timer = QBasicTimer()
		self._timer.start(1000 // 60, self)


	def init_layout(self):
		# Load styles
		self.setStyleSheet('background-color: #141414')
		
		#pane_styles = background-color: #

		text_styles = '''
			color: #70737b;
			font-family: mono;
			font-size: 10px;
			font-weight: bold;
		'''

		self.image = QLabel()
		
		time_axis = QWidget()
		#time_axis.setStyleSheet('background-color: #1a1a1b;')
		time_axis.setFixedHeight(AXIS_HEIGHT)

		for i in range(SPEC_WIDTH // SECONDS_WIDTH + 1):
			# Add ticks
			n_ticks = 20
			for j in range(n_ticks):
				if j in [1, 2, 3]:
					continue
				tick = QWidget(time_axis)
				tick.setStyleSheet(f'''
					background-color: {'#4a4a4f' if j == 0 else '#25252c'};
				''')
				tick.setGeometry(
					SPEC_WIDTH - (i+1) * SECONDS_WIDTH + int(SECONDS_WIDTH / n_ticks * j),
					6,
					1,
					AXIS_HEIGHT-6*2)
			# Add seconds text	
			time = QLabel(f'-{i+1}s', time_axis)
			time.setStyleSheet(text_styles)
			time.move(SPEC_WIDTH - (i+1) * SECONDS_WIDTH + 8, 6)
		
		freq_axis = QWidget()
		#freq_axis.setStyleSheet('background-color: #1a1a1b;')
		freq_axis.setFixedWidth(AXIS_WIDTH)
		
		for freq in [0, 2500, 5000, 7500, 10000]:
			# Add ticks
#			n_ticks = 20
#			for j in range(n_ticks):
#				if j in [1, 2, 3]:
#					continue
			tick = QWidget(freq_axis)
			tick.setStyleSheet(f'''
				background-color: {'#4a4a4f'};
			''')
			tick.setGeometry(
				AXIS_WIDTH-4-3,
				int(SPEC_HEIGHT - (freq / (sample_rate / 2)) * SPEC_HEIGHT),
				4,
				1)
			# Add seconds text	
			time = QLabel(f'{freq}hz', freq_axis)
			time.setStyleSheet(text_styles)
			time.setGeometry(0, int(SPEC_HEIGHT - (freq / (sample_rate / 2)) * SPEC_HEIGHT)-5, AXIS_WIDTH-12, 10)
			time.setAlignment(Qt.AlignRight |Qt.AlignVCenter)
			
			print(time.width())
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



	def timerEvent(self, event):
		temp_spec = self.spec.copy()
		temp_spec[:,:-1] = self.spec[:,1:]

		window = data[self.index*HOP_SIZE:self.index*HOP_SIZE + WINDOW_SIZE]
		
		if window.size != 512:
			return

		strip = calc_strip(window)
		colored_strip = color_map(strip)[:,:3]
		colored_uints = (colored_strip * 255).astype(np.uint8)
		temp_spec[:, -1, :] = colored_uints#color_map(strip)[:,:3]
		
		self.index += 1

		self.update_spec(temp_spec)


	def update_spec(self, spec):
		self.spec = spec
		h, w, c = self.spec.shape
		new_image = QImage(self.spec.data, w, h, c*w, QImage.Format_RGB888)
		self.image.setPixmap(QPixmap(new_image))



		#self.addWidget(image)

#		self.setMinimumWidth(940)
#		self.setMinimumHeight(560)

#		props = {
#			'on_navigate': self.on_navigate
#		}

#		login     = Login(props, self)
#		dashboard = Dashboard(self.on_navigate, self)
		
#		self.editor = Editor(self.on_navigate, self)

#		self.stack = QStackedWidget(self)
#		self.stack.addWidget(login)
#		self.stack.addWidget(dashboard)
#		self.stack.addWidget(self.editor)

#		layout = QGridLayout(self)
#		layout.setContentsMargins(0, 0, 0, 0)
#		layout.setSpacing(0)
#		layout.addWidget(self.stack)
		
#		self.stack.setCurrentIndex(2)
#		self.stack.setCurrentIndex(0)

#	def on_navigate(self, i):
#		self.stack.setCurrentIndex(i)

#		button_spectator.setEnabled(False)
#		button_spectator.clicked.connect(lambda : self.select_type(''))
#		#
#		# Layouts
#		#
#		scroll = QScrollArea()
#		scroll.setStyleSheet('background-color: #151617')
#		#scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
#		scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
#		scroll.setWidget(video_widget)
#
#		vbox = QVBoxLayout()
#		vbox.setSpacing(24)
#		vbox.addWidget(scroll)
#		vbox.addLayout(hbox)
#
#		self.setLayout(vbox)
#		# Position window
#		center = QDesktopWidget().availableGeometry().center()
#		rect = self.frameGeometry()
#		rect.moveCenter(center)
#		self.move(rect.x(), 180)
#		# Use stylesheet

#		self.video = None
	
#		for i, button in enumerate(self.video_buttons):
#			if i == index:
#				button.setStyleSheet('border: 2px solid #2f5')
#			else:
#				button.setStyleSheet('background-color: none; border: none;')
#
	def keyPressEvent(self, event):
		#super().keyPressEvent(event)
#		if event.isAutoRepeat():
#			return
		
		if event.key() == Qt.Key_Escape:
			self.close()
		
#		if self.stack.currentWidget() == self.editor:
			
#			captured = self.editor.player.keyPressEvent(event)
#			if captured:
#				return
			
#			if event.key() == Qt.Key_D:
#				self.editor.player.panorama.debug = not self.editor.player.panorama.debug
#				self.editor.player.panorama.update_view()
			
#			if event.key() == Qt.Key_C:
#				frame = self.editor.player.snap((1280, 720))[:,:,::-1]
#				Image.fromarray(frame).save('50-nonconcentric-right-edge.png')
			
#			if event.key() == Qt.Key_E:
#				self.editor.player.endgame.toggle()
#			
#			if event.key() == Qt.Key_F:
#				self.editor.player.show_field = not self.editor.player.show_field
			
#			if event.key() == Qt.Key_G:
#				self.editor.player.goal.toggle()
#			
#			if event.key() == Qt.Key_H:
#				self.editor.player.halftime.toggle()
#			
#			if event.key() == Qt.Key_P:
#				self.editor.player.pregame.toggle()
#			
#			if event.key() == Qt.Key_S:
#				self.editor.player.score.toggle()
#			
#			if event.key() == Qt.Key_Space:
#				self.editor.player.on_play_pause()
#
#			if event.key() == Qt.Key_Left:
#				self.editor.player.reader.jump(-30 * 20)
#			
#			if event.key() == Qt.Key_Right:
#				self.editor.player.reader.jump(30 * 20)

		#key_map = {
		#	Qt.Key_Left:   self.jump_left,
		#	Qt.Key_Right:  self.jump_right,
		#	Qt.Key_T:      self.add_track,
		#	Qt.Key_Comma:  self.prev_track,
		#	Qt.Key_Period: self.next_track,
		#	Qt.Key_J:      self.press_jump,
		#	Qt.Key_R:      self.remove_label,
		#	Qt.Key_F:      self.fill_previous,
		#	Qt.Key_H:      self.press_repeat,
		#}
		#if event.key() in key_map:
		#	key_map[event.key()]()





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







