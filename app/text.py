import freetype
import numpy as np

from utils import orthographic


SCALE = 2
FONT_SIZE = 12

# Adapted frpm this answer
#	https://stackoverflow.com/questions/63836707/how-to-render-text-with-pyopengl


class CharacterSlot:

	def __init__(self, ctx, glyph):
		if not isinstance(glyph, freetype.GlyphSlot):
			raise RuntimeError('Unknown glyph type')

		self.width   = glyph.bitmap.width
		self.height  = glyph.bitmap.rows
		self.advance = glyph.advance.x

		size = (self.width, self.height)

		data = np.array(glyph.bitmap.buffer, dtype='u1')
		self.texture = ctx.texture(size, 1, data)
		self.texture.repeat_x = False
		self.texture.repeat_y = False


class Text:

	VERTEX = '''
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
		in vec2 v_uv;
		uniform sampler2D image;
		uniform vec4 color;
		out vec4 out_color;
		void main() {
			float mask = texture(image, v_uv).r;
			out_color = vec4(color.rgb, color.a * mask);
		}
	'''

	def __init__(self, ctx):
		self.ctx = ctx
		self.prog = self.ctx.program(
				vertex_shader=self.VERTEX,
				fragment_shader=self.FRAGMENT)

		self.vbo = self.ctx.buffer(
				reserve=6*4*4, dynamic=True)

		self.vao = self.ctx.vertex_array(
				self.prog, self.vbo, 'vertex', 'uv')
		
		self.prog['color'] = (0.5, 0.5, 0.55, 1)

		self.init_font('fonts/Rubik-Regular.ttf')

		self.texts = []

	def init_font(self, font):
		self.characters = dict()
		size = int(FONT_SIZE * SCALE)
		# Load the font face
		face = freetype.Face(font)
		face.set_pixel_sizes(size, size)
		# Load ASCII characters from 30-128
		for i in range(30, 128):
			char = chr(i)
			face.load_char(char)
			character = CharacterSlot(self.ctx, face.glyph)
			self.characters[char] = character

	def set_geometry(self, x, y, w, h):
		vertices = np.array([
			x,   y,   0, 1,
			x+w, y,   1, 1,
			x+w, y-h, 1, 0,
			x,   y,   0, 1,
			x+w, y-h, 1, 0,
			x,   y-h, 0, 0,
		])
		vertices = vertices.astype('f4')
		self.vbo.write(vertices)

	def text_width(self, text):
		w = 0
		for c in text:
			character = self.characters[c]
			w += (character.advance >> 6) / SCALE
		return w

	def add(self, text, x, y, align='left'):
		self.texts.append((text, x, y, align))

	def size(self, w, h):
		P = orthographic(w, h)
		self.prog['P'].write(P)

	def draw(self):
		for text, x, y, align in self.texts:
			if align == 'center':
				w = self.text_width(text)
				x -= w / 2
			if align == 'right':
				w = self.text_width(text)
				x -= w
			for i, c in enumerate(text):
				character = self.characters[c]
				character.texture.use(0)
				w = character.width
				h = character.height
				self.set_geometry(x, y, w / SCALE, h / SCALE)
				self.vao.render()
				x = x + (character.advance >> 6) / SCALE



