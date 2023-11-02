
import moderngl
import numpy as np

from utils import orthographic

class Ticks:

	VERTEX = '''
		#version 330 core
		uniform mat4 P;
		in vec2 vertex;
		void main() {
			gl_Position = P * vec4(vertex, 0, 1);
		}
	'''

	FRAGMENT = '''
		#version 330 core
		uniform vec4 color;
		out vec4 out_color;
		void main() {
			out_color = color;
		}
	'''

	def __init__(self, ctx, x, y, w, h, color=(1,0,1,1), gap=50, horizontal=True):
		self.ctx = ctx
		self.x = x
		self.y = y
		self.w = w
		self.h = h
		self.prog = self.ctx.program(
				vertex_shader=self.VERTEX,
				fragment_shader=self.FRAGMENT)
		self.prog['color'] = color

		if horizontal:
			n = int(w) // int(gap) + 1
		else:
			n = int(h) // int(gap) + 1

		vertices = np.zeros(n * 4, dtype='f4')

		for i in range(0, n):
			if horizontal:
				vertices[i*4:(i+1)*4] = [
					x + i * gap, y,
					x + i * gap, y + h
				]
			else:
				vertices[i*4:(i+1)*4] = [
					x,     y + i * gap,
					x + w, y + i * gap
				]
		buffer = self.ctx.buffer(vertices)
		self.vao = self.ctx.vertex_array(
				self.prog, buffer, 'vertex')

	def size(self, w, h):
		P = orthographic(w, h)
		self.prog['P'].write(P)

	def draw(self):
		self.vao.render(moderngl.LINES)


