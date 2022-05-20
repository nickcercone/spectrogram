import moderngl
import numpy as np
import pyrr
from PIL import Image
from PyQt5.QtCore import Qt, QBasicTimer
from PyQt5.QtGui import QSurfaceFormat
from PyQt5.QtWidgets import QApplication, QOpenGLWidget




class Surface(QOpenGLWidget):

	def __init__(self):
		super().__init__()
		# Set GL Version 3.3 core
		fmt = QSurfaceFormat()
		fmt.setVersion(3, 3)
		fmt.setProfile(QSurfaceFormat.CoreProfile)
		fmt.setDefaultFormat(fmt)
		fmt.setSamples(4)
		self.setFormat(fmt)

#		self._timer = QBasicTimer()
#		self._timer.start(1000 // 31, self)

	def initializeGL(self):
		self.ctx = moderngl.create_context(require=330)
		# Set background color
		self.ctx.clear(0.0, 0.0, 0.0)
		# Enable blending / transparency
		self.ctx.enable(moderngl.BLEND)
		self.ctx.blend_func = self.ctx.SRC_ALPHA, self.ctx.ONE_MINUS_SRC_ALPHA
		# Needed for antialiasing
		self.ctx.multisample = True
		#self.fbo = self.ctx.detect_framebuffer()
		#self.ctx.disable(moderngl.CULL_FACE)
		#print('OpenGL Version:', self.ctx.version_code)
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

		# Create Shader Program
		self.prog = self.ctx.program(vertex_shader=vertex, fragment_shader=fragment)
		
		P = pyrr.Matrix44.orthogonal_projection(0, 1024, 0, 256, 1, -1).astype('f4')
		
		# Orthogonal Matrix
		self.prog['orth'].write(P)
		self.prog['image'].value = 0

		vertices = np.array([
			0-0.5,      0, 0.0, 1.0,
			1024+0.5,   0, 1.0, 1.0,
			1024+0.5, 256, 1.0, 0.0,
			0-0.5,      0, 0.0, 1.0,
			1024+0.5, 256, 1.0, 0.0,
			0-0.5,    256, 0.0, 0.0
		]).astype('f4')
		
		# Vertex Buffer Aray
		self.vbo = self.ctx.buffer(vertices.tobytes())
		
		# Vertex Attribute Array
		self.vao = self.ctx.vertex_array(self.prog, self.vbo, 'vertex')
		# Texture
		self.texture = self.ctx.texture((1024, 256), 3)#frame.shape[1::-1], frame.shape[2], frame)
		
		#frame = (np.random.random((256, 1024, 3)) * 255).astype(np.uint8)
		#self.set_texture(frame)

	def set_texture(self, frame):
		if hasattr(self, 'texture'):
			self.texture.release()
			self.texture = None
		#print('set_texture')
		self.texture = self.ctx.texture(frame.shape[1::-1], frame.shape[2], frame)
		self.texture.use(0)
				
		self.update()
#		self.vao.render()
		#print('hello')
		#self.texture.use(0)
		#self.texture.release()
		#self.texture.write(frame)
		#self.texture.use(0)

	def paintGL(self):

#		frame = (np.random.random((256, 1024, 3)) * 255).astype(np.uint8)
#		self.set_texture(frame)
		#pass
		#self.prog['image'].value = 0
		self.texture.use(0)
		self.vao.render()
	#self.texture.use(0)
		#self.vao.render()

	def timerEvent(self, event):
		self.update()
	
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
	main = Surface()
	main.resize(1024, 256)
	main.show()
	
	# Run main loop
	app.exit(app.exec())








