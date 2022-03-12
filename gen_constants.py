#!/usr/bin/env python3
from constants_in import *
import math
import random
import gzip
from modules import bits

# Scale factor should be such that it increases by a factor of LOOP_SCALE every LOOP_LENGTH frames
#  scale = A * LOOP_SCALE^(t/LOOP_LENGTH)
#  scale = A * exp(log(LOOP_SCALE)/LOOP_LENGTH * t)
SCALE_K = math.log(LOOP_SCALE)/LOOP_LENGTH
# Scale constant should be such that, at t=INIT_NO_SCALE, the scale is equal to INIT_SCALE
#  INIT_SCALE = A * exp(k*INIT_NO_SCALE)
SCALE_A = INIT_SCALE / math.exp(SCALE_K * INIT_NO_SCALE)

# Time scale factor should be such that it increases by a factor of LOOP_TIMESCALE every LOOP_LENGTH frames
TIMESCALE_K = math.log(LOOP_TIMESCALE)/LOOP_LENGTH
# Time scale constant should be such that, at t=0, it is increasing at a rate of approx 1 per second
#  d/dt A*exp(k*t) |t=0 = 1/FPS
#  A*k*exp(k*0) = 1/FPS
TIMESCALE_A = 1/FPS/TIMESCALE_K
# But round off so we're starting at the same point at every level of the nesting
TIMESCALE_A = round(TIMESCALE_A) * LOOP_TIMESCALE / (LOOP_TIMESCALE-1)

# Pre-generate the list of which frames of the render correspond to which frames of the tile graphics
above = []
current = []
below = []
for t in range(LOOP_LENGTH):
	x = TIMESCALE_A * math.exp(TIMESCALE_K * t)
	above.append(int(x) // LOOP_TIMESCALE)
	current.append(int(x) % LOOP_TIMESCALE)
	below.append(int(x * LOOP_TIMESCALE) % LOOP_TIMESCALE)
FRAMES = above + current + below
# For the first couple loops through, use the accurate tile frame numbers
# but after that, fudge towards reusing existing frames
# so that we don't have to extract as many frames
# at that point the animation's going so quick that it doesn't matter if it's slightly off
count_first_frame = current.count(current[0])
usable_tiles = list(set(above + current + below[:count_first_frame]))
usable_tiles.sort()
nearest_usable = {}
for i in range(0, usable_tiles[0]):
	nearest_usable[i] = usable_tiles[0]
for a,b in zip(usable_tiles, usable_tiles[1:]):
	mid = (a + b + 1) // 2
	for i in range(a, mid):
		nearest_usable[i] = a
	for i in range(mid, b):
		nearest_usable[i] = b
for i in range(usable_tiles[-1], LOOP_TIMESCALE):
	nearest_usable[i] = usable_tiles[-1]
FRAMES = [nearest_usable[i] for i in FRAMES]

# Find all the active tiles in the top-level tile, these are places where we can recurse
with gzip.open("tile_on.gz", "rb") as fp:
	tile = bits.BitGrid.load(fp)
top_triangle = []
bottom_triangle = []
other = []
# classify them by regions
for y in range(EDGE_BUFFER, LOOP_SCALE - EDGE_BUFFER):
	for x in range(EDGE_BUFFER, LOOP_SCALE - EDGE_BUFFER):
		if tile[x,y]:
			if is_top_triangle(x, y):
				top_triangle.append((x, y))
			elif is_bottom_triangle(x, y):
				bottom_triangle.append((x, y))
			else:
				other.append((x, y))
# sanity-check the hard-coded locations
all_valid_centers = set(top_triangle + bottom_triangle + other)
for i in FIRST_CENTRES:
	if i not in all_valid_centers:
		raise ValueError(f"{i} is not valid for FIRST_CENTRES")
# generate more locations
CENTRES = list(FIRST_CENTRES)
rand = random.Random(SEED)
for i in range(len(FIRST_CENTRES), LOOP_COUNT + 2):
	section = rand.choices([top_triangle, bottom_triangle, other], [WEIGHT_TOP_TRIANGLE, WEIGHT_BOTTOM_TRIANGLE, WEIGHT_OTHER])[0]
	CENTRES.append(rand.choice(section))
# generate context for the very first centre
TOPLEVEL_CONTEXT = tile.context(FIRST_CENTRES[0])

# generate float versions of the centre locations, which are affected by all the lower centres
x, y = CENTRES[0]
x *= LOOP_SCALE / (LOOP_SCALE - 1)
y *= LOOP_SCALE / (LOOP_SCALE - 1)
CENTRES_FLOAT = [(x, y)]
for cx, cy in CENTRES:
	x = cx + x / LOOP_SCALE
	y = cy + y / LOOP_SCALE
	CENTRES_FLOAT.append((x, y))

with open("constants.py", "w") as fp:
	print(f"{WIDTH=!r}", file=fp)
	print(f"{HEIGHT=!r}", file=fp)
	print(f"{FPS=!r}", file=fp)
	print(f"{OSA=!r}", file=fp)
	print(f"{LOOP_SCALE=!r}", file=fp)
	print(f"{LOOP_LENGTH=!r}", file=fp)
	print(f"{LOOP_COUNT=!r}", file=fp)
	print(f"{INIT_NO_SCALE=!r}", file=fp)
	print(f"{SCALE_A=!r}", file=fp)
	print(f"{SCALE_K=!r}", file=fp)
	print(f"{FRAMES=!r}", file=fp)
	print(f"{CENTRES=!r}", file=fp)
	print(f"{CENTRES_FLOAT=!r}", file=fp)
	print(f"{TOPLEVEL_CONTEXT=!r}", file=fp)
	print(f"{EDGE_BUFFER=!r}", file=fp)
	print(f"{BLOOM=!r}", file=fp)

with open("constants.h", "w") as fp:
	print(f"const int WIDTH = {WIDTH!r};", file=fp)
	print(f"const int HEIGHT = {HEIGHT!r};", file=fp)
	print(f"const int FPS = {FPS!r};", file=fp)
	print(f"const int OSA = {OSA!r};", file=fp)
	print(f"const int LOOP_SCALE = {LOOP_SCALE!r};", file=fp)
	print(f"const int LOOP_LENGTH = {LOOP_LENGTH!r};", file=fp)
	print(f"const int LOOP_COUNT = {LOOP_COUNT!r};", file=fp)
	print(f"const int INIT_NO_SCALE = {INIT_NO_SCALE!r};", file=fp)
	print(f"const double SCALE_A = {SCALE_A!r};", file=fp)
	print(f"const double SCALE_K = {SCALE_K!r};", file=fp)
	print(f"const int FRAMES[] = {{{', '.join(repr(i) for i in FRAMES)}}};", file=fp)
	print(f"const int CENTRESX[] = {{{', '.join(repr(i[0]) for i in CENTRES)}}};", file=fp)
	print(f"const int CENTRESY[] = {{{', '.join(repr(i[1]) for i in CENTRES)}}};", file=fp)
	print(f"const double CENTRES_FLOATX[] = {{{', '.join(repr(i[0]) for i in CENTRES_FLOAT)}}};", file=fp)
	print(f"const double CENTRES_FLOATY[] = {{{', '.join(repr(i[1]) for i in CENTRES_FLOAT)}}};", file=fp)
	print(f"const int TOPLEVEL_CONTEXT = {TOPLEVEL_CONTEXT!r};", file=fp)
	print(f"const int EDGE_BUFFER = {EDGE_BUFFER!r};", file=fp)
	print(f"const double BLOOM = {BLOOM!r};", file=fp)

with open("constants.lua", "w") as fp:
	print("local constants = {}", file=fp)
	print(f"constants.FRAMES = {{{', '.join(repr(f) for f in sorted(set(FRAMES)))}}}", file=fp)
	print(f"constants.FRAME_OFFSET = {FRAME_OFFSET}", file=fp)
	print("return constants", file=fp)
