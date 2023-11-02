import config

from rect import Rect
from source import File, Microphone
from spec import Spec
from text import Text
from ticks import Ticks
from wave import Wave
from window import Window

from utils import logger


class App(Window):

	def init(self):
		logger.info(f'init')
		#self.source = File('audio/gettysburg.wav')
		self.source = Microphone()

		self.nodes = []

		self.wave = Wave(self.ctx, 0, 0, config.WINDOW_WIDTH, 200)
		self.nodes.append(self.wave)

		self.spec = Spec(self.ctx, 0, self.wave.h, config.WINDOW_WIDTH, 460)
		self.nodes.append(self.spec)

		bg_color = (0.06, 0.06, 0.07, 1)


		# Wave spec separation line
		self.nodes.append(
			Rect(self.ctx, 0, self.wave.h, config.WINDOW_WIDTH, 3, bg_color)
		)

		# Time axis background
		self.nodes.append(
			Rect(self.ctx, 0, 660, config.WINDOW_WIDTH, 70, bg_color)
		)
		# Frequency axis background
		self.nodes.append(
			Rect(self.ctx, 0, 0, 80, config.WINDOW_HEIGHT, bg_color)
		)

		# Ticks
		
		# 1/20th second ticks
		self.nodes.append(
			Ticks(self.ctx, x=81, y=660, w=1200, h=15, color=(0.3,0.3,0.4,1), gap=6)
		)

		# 1 second ticks
		self.nodes.append(
			Ticks(self.ctx, x=81, y=660, w=1200, h=25, color=(0.4,0.4,0.5,1), gap=120)
		)

		# 2000 Hz Ticks
		pixels_per_freq = self.spec.h / 11046
		self.nodes.append(
			Ticks(
				self.ctx,
				x=70,
				y=self.spec.y + pixels_per_freq * 1046,
				w=10,
				h=pixels_per_freq * 10000,
				color=(0.4,0.4,0.5,1),
				gap=pixels_per_freq * 2000,
				horizontal=False)
		)

		# Text

		# Create text renderer
		text = Text(self.ctx)
		self.nodes.append(text)

		# Seconds text
		for i in range(1, 11):
			x = config.WINDOW_WIDTH - i * 120
			text.add(f'{i}s', x, 705, align='center')
		
		# Hz text
		for i in range(6):
			hz = i * 2000
			y = 660 - pixels_per_freq * hz + 4
			text.add(f'{hz}hz', 62, y, align='right')

	def size(self, w, h):
		logger.info(f'size {w} {h}')
		for node in self.nodes:
			node.size(w, h)

	def draw(self, dt):
		available = self.source.available()
		
		logger.info(f'{available}')

		for i in range(2):
			window = self.source.get()
			self.wave.add(window)
			self.spec.add(window)

		self.wave.update()
		self.spec.update()

		for node in self.nodes:
			node.draw()

	def exit(self):
		logger.info('exit')
		self.source.release()



if __name__ == '__main__':
	App.run()
