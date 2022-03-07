SMALL_MODE = True

if SMALL_MODE:
	WIDTH = 640
	HEIGHT = 360
	OSA = 1
else:
	# Render size: 4K60 sounds good to me
	WIDTH = 3840
	HEIGHT = 2160
	# Oversample a cross with 4 dots per diagonal
	#OSA = 4
	OSA = 1
FPS = 60

# How long to spend each level
LOOP_LENGTH = 80*FPS
# How many loops to generate (this adds up to 1 hour)
LOOP_COUNT = 45
# Initial zoom should be so that there are about 5 spaceships across, and they're 23 cells apart
INIT_SCALE = 5*23
# Don't zoom in for the first 3 seconds of the video
INIT_NO_SCALE = 3*FPS

# How much to scale up each level
# These are the stats for the size/period of the metacell
LOOP_SCALE = 2048
LOOP_TIMESCALE = 35328
# How many generations to skip before starting the loop, because the full period doesn't start straight away
FRAME_OFFSET = 4097

# Fixed seed so that re-running gen script is deterministic
SEED = 123456
# Set the first few centres for the right effect, before going random
FIRST_CENTRES = [(1767,1030), (1767,1030), (1007,270), (1612,1830), (53, 1172)]
# Random area weights
WEIGHT_BOTTOM_TRIANGLE = 8
WEIGHT_TOP_TRIANGLE = 3
WEIGHT_OTHER = 1
is_bottom_triangle = lambda x,y: x < 1925 and y < 1833 and x+y > 2040
is_top_triangle = lambda x,y: x > 205 and y > 112 and x+y < 2040
# Don't pick centres within this distance of the edge of the tile
EDGE_BUFFER = 50

# Expand cells slightly so they overlap
# Multiplies the size of each pixel by this factor
# If this is too low, it causes Moiré effects as the zoom changes
# IF this is too high, the fine detail becomes a blobby mess as it zooms out
if SMALL_MODE:
	BLOOM = 1.1
else:
	BLOOM = 2

