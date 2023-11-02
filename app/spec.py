import config
import librosa
import matplotlib
import moderngl
import numpy as np
import time

from utils import orthographic


hann = np.hanning(config.WINDOW_SIZE)

color_map = matplotlib.colormaps.get_cmap('inferno')



def stft_slice(window):
	n = window.shape[0]
	if n < config.WINDOW_SIZE:
		padded = np.zeros(config.WINDOW_SIZE, dtype=window.dtype)
		padded[:n] = window
		window = padded
	tapered = window * hann
	return np.fft.rfft(tapered)

def stft_color(slice, min_db=-30, max_db=30):
	slice = np.abs(slice)
	slice = librosa.amplitude_to_db(slice)
	slice = slice.clip(min_db, max_db)
	slice = (slice - min_db) / (max_db - min_db)
	slice = color_map(slice)
	slice = (slice * 255).astype('u1')
	slice = slice[:, :3]
	return slice


class Spec:

	VERTEX= '''
		#version 330 core
		uniform mat4 P;
		in vec2 vertex;
		in vec2 uv;
		out vec2 v_uv;
		void main() {
			gl_Position = P * vec4(vertex, 0, 1);
			v_uv = uv;
		}
	'''

	FRAGMENT = '''
		#version 330 core
		uniform sampler2D image;
		in vec2 v_uv;
		out vec4 out_color;
		void main() {
			vec4 color = texture(image, v_uv);
			out_color = vec4(color.rgb, 1);
		}
	'''

	def __init__(self, ctx, x, y, w, h):
		self.ctx = ctx
		self.x = x
		self.y = y
		self.w = w
		self.h = h
		self.prog = self.ctx.program(
				vertex_shader=self.VERTEX,
				fragment_shader=self.FRAGMENT)

		vertices = np.array([
			0, y,   0, 1, # A
			0, y+h, 0, 0, # B
			w, y+h, 1, 0, # C
			0, y,   0, 1, # A
			w, y+h, 1, 0, # C
			w, y,   1, 1, # D
		])

		vertices = vertices.astype('f4')
		buffer = self.ctx.buffer(vertices)
		self.vao = self.ctx.vertex_array(
				self.prog, buffer, 'vertex', 'uv')

		self.frame = np.zeros((513, self.w, 3), dtype='u1')

		self.texture = self.ctx.texture(
				size=(self.w, 513),
				components=3,
				data=self.frame)
		self.texture.repeat_x = False
		self.texture.repeat_y = False

		self.slice = np.zeros((513, 3), dtype='u1')

	def add(self, window):
		self.frame[:,:-1,:] = self.frame[:,1:,:]
		if window is not None:
			slice = stft_slice(window)
			slice = stft_color(slice)
			self.slice = slice
		self.frame[:,-1,:] = self.slice

	def update(self):
		self.texture.write(self.frame)

	def size(self, w, h):
		P = orthographic(w, h)
		self.prog['P'].write(P)

	def draw(self):
		self.texture.use(0)
		self.vao.render()






