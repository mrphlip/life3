SMALL_MODE = False

if SMALL_MODE:
	WIDTH = 640
	HEIGHT = 360
	OSA = 1
else:
	# Render size: this is the resolution of 4K video
	WIDTH = 3840
	HEIGHT = 2160
	# Oversampling level - renders multiple pixels per pixel and averages them, to get
	# feathered edges and shades of grey. If this is set to 1, you'll get pure B&W
	# output with hard edges.
	OSA = 3
FPS = 60

# How much time to spend each level of the nesting, measured in frames
LOOP_LENGTH = 80*FPS
# How many loops to generate (80 seconds per loop * 45 loops = 1 hour)
LOOP_COUNT = 45
# Set initial zoom such that there are about 5 spaceships across, and they're 23 cells apart
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
# Changing this will make it generate a different sequence of zoom-out centre points
SEED = 123456
# Manually set the first few centres, all the following ones are random
# This is:
#   * two zooms out at the same position (near the original video)
#   * one zoom out on the upper half of the grid, where the spaceships are moving vertically
#   * one zoom out on a spaceship right at the bottom of the grid, so some outer machinery is visible
#   * one zoom out in the outer machinery around the edge of the cell
# Note that for the animation to make sense, this must be the position of a cell
# that is *on* at the start of the animation.
# gen_constants.py will check this, and refuse if you pick a cell that is off.
# Look at tile_on.png in an image editor to check your coordinates.
FIRST_CENTRES = [(1767,1030), (1767,1030), (1007,270), (1612,1830), (53, 1172)]
# Random area weights - how likely is it to pick a cell in each of these regions?
WEIGHT_BOTTOM_TRIANGLE = 8
WEIGHT_TOP_TRIANGLE = 3
WEIGHT_OTHER = 1
# define the different regions of the image
is_bottom_triangle = lambda x,y: x < 1925 and y < 1833 and x+y > 2040
is_top_triangle = lambda x,y: x > 205 and y > 112 and x+y < 2040
# Don't pick centres within this distance of the edge of the tile
# Should be around half of INIT_SCALE, to ensure we don't zoom out to see the
# edge of the metacell before it's ready
EDGE_BUFFER = 50

# Expand cells slightly so they overlap
# Multiplies the size of each pixel by this factor
# If this is too low, it causes Moiré effects as the zoom changes
# IF this is too high, the fine detail becomes a blobby mess as it zooms out
if SMALL_MODE:
	BLOOM = 1.25
else:
	BLOOM = 5
