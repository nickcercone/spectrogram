import numpy as np
import os
from functools import partial
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon, QImage, QPixmap
from PyQt5.QtWidgets import QApplication, QWidget, QGridLayout, QStackedWidget, QLabel, QVBoxLayout
#from widgets.login import Login
#from widgets.dashboard import Dashboard
#from widgets.editor import Editor


#from utils.const import assets
#from utils.style import THEME

#from PIL import Image





class Main(QWidget):

	def __init__(self):
		super().__init__()
		# Load styles
#		self.setStyleSheet(THEME)
		self.setStyleSheet("background-color: #0a0a0b")
		#icon_file = os.path.join(ASSETS, 'images/icon.png')
#		icon_file = assets('images/icon.png')
		
#		self.setWindowTitle('Dribl Vision')
#		self.setWindowIcon(QIcon(icon_file))
#		self.resize(1280, 720)
		self.setFixedSize(1280, 720)
		

		frame = np.random.random((700, 700, 3))
		frame = (frame * 255).astype(np.uint8)

		height, width, channel = frame.shape
		bytes_per_line = channel * width
		q_image = QImage(frame.data, width, height, bytes_per_line, QImage.Format_RGB888)

		image = QLabel(self)
		image.setPixmap(QPixmap(q_image))

		

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







