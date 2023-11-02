import logging
from pyrr import Matrix44

#------------
#	Logger
#------------

# Create custom logger
logger = logging.getLogger('spectrogram')

# Set level
#logger.setLevel(logging.INFO)
logger.setLevel(logging.ERROR)

# Create handler
handler = logging.StreamHandler()

# Set foratter
format = '%(asctime)s - %(levelname)s - %(filename)s - %(message)s'
formatter = logging.Formatter(format)
handler.setFormatter(formatter)

# Add handler to the logger
logger.addHandler(handler)



#----------------
#	Projection
#----------------


def orthographic(w, h):
	return Matrix44.orthogonal_projection(
			0, w, h, 0, 1, -1, dtype='f4')

