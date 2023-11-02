import numpy as np

from utils import orthographic


class Rect:

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

	def __init__(self, ctx, x, y, w, h, color=(0, 0.5, 1, 1)):
		self.ctx = ctx
		self.x = x
		self.y = y
		self.w = w
		self.h = h
		self.prog = self.ctx.program(
				vertex_shader=self.VERTEX,
				fragment_shader=self.FRAGMENT)

		self.prog['color'] = color

		vertices = np.array([
			x,   y,
			x+w, y,
			x+w, y+h,
			x,   y,
			x+w, y+h,
			x,   y+h,
		])
		vertices = vertices.astype('f4')
		buffer = self.ctx.buffer(vertices)
		self.vao = self.ctx.vertex_array(self.prog, buffer, 'vertex')

	def size(self, w, h):
		P = orthographic(w, h)
		self.prog['P'].write(P)

	def draw(self):
		self.vao.render()


