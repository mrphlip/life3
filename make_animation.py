#!/usr/bin/env python3
import math
import gzip
import constants
import subprocess
import os
from modules.bits import BitGrid

GRID_CACHE = {}
def get_grid(context, frame):
	#context = constants.TOPLEVEL_CONTEXT
	#context = 16 if context & 0x10 else 7
	#frame = 0
	if (context, frame) not in GRID_CACHE:
		with gzip.open(f"tiles/{context}/{frame}.gz", "rb") as fp:
			GRID_CACHE[context, frame] = BitGrid.load(fp)
	return GRID_CACHE[context, frame]

def clear_cache():
	GRID_CACHE.clear()

def split_range(valmin, valmax):
	ivalmin = math.floor(valmin)
	fvalmin = valmin - ivalmin
	ivalmax = math.ceil(valmax) - 1
	fvalmax = valmax - ivalmax
	if ivalmin == ivalmax:
		yield ivalmin, fvalmin * constants.LOOP_SCALE, fvalmax * constants.LOOP_SCALE
		return
	yield ivalmin, fvalmin * constants.LOOP_SCALE, constants.LOOP_SCALE
	for i in range(ivalmin + 1, ivalmax):
		yield i, 0.0, constants.LOOP_SCALE
	yield ivalmax, 0.0, fvalmax * constants.LOOP_SCALE

def is_covered(depth, frame, depthofs, depthmax, xmin, xmax, ymin, ymax, context=None):
	if depthofs >= 2:
		context = constants.TOPLEVEL_CONTEXT
		frameix = 0
	else:
		frameix = frame + constants.LOOP_LENGTH * (1 - depthofs)
	tile = get_grid(context, constants.FRAMES[frameix])
	if depthofs <= depthmax:
		return tile.is_covered((math.floor(xmin), math.floor(ymin)), (math.ceil(xmax), math.ceil(ymax)))
	else:
		splity = list(split_range(ymin, ymax))
		splitx = list(split_range(xmin, xmax))
		for y, newymin, newymax in splity:
			for x, newxmin, newxmax in splitx:
				if is_covered(depth, frame, depthofs - 1, depthmax,
						newxmin, newxmax, newymin, newymax, tile.context((x, y))):
					return True
		return False

def render_pixel_level(depth, frame, depthmax, xmin, xmax, ymin, ymax):
	for i in range(2):
		cx, cy = constants.CENTRES[depth + i]
		xmin = cx + (xmin / constants.LOOP_SCALE)
		xmax = cx + (xmax / constants.LOOP_SCALE)
		ymin = cy + (ymin / constants.LOOP_SCALE)
		ymax = cy + (ymax / constants.LOOP_SCALE)
	if is_covered(depth, frame, 2, depthmax, xmin, xmax, ymin, ymax):
		return 1.0
	else:
		return 0.0

def render_pixel(depth, frame, xmin, xmax, ymin, ymax):
	if depth >= 1 and frame < constants.INIT_NO_SCALE:
		p0 = render_pixel_level(depth, frame, 0, xmin, xmax, ymin, ymax)
		p1 = render_pixel_level(depth, frame, -1, xmin, xmax, ymin, ymax)
		prop = frame / constants.INIT_NO_SCALE
		return p1 * (1 - prop) + p0 * prop
	else:
		return render_pixel_level(depth, frame, 0, xmin, xmax, ymin, ymax)

def render_pixel_osa(depth, frame, xmin, xmax, ymin, ymax):
	dx = (xmax - xmin) / 2
	dy = (ymax - ymin) / 2
	cx = (xmin + xmax) / 2
	cy = (ymin + ymax) / 2
	bloomx = dx * constants.BLOOM
	bloomy = dx * constants.BLOOM
	if constants.OSA <= 1:
		return render_pixel(depth, frame, cx - bloomx, cx + bloomx, cy - bloomy, cy + bloomy)
	dat = 0
	for n in range(constants.OSA):
		px = xmin + dx * (2 * n + 1) / constants.OSA
		py = ymin + dy * (2 * n + 1) / constants.OSA
		dat += render_pixel(depth, frame, px - bloomx, px + bloomx, py - bloomy, py + bloomy)
		py = ymax - dy * (2 * n + 1) / constants.OSA
		dat += render_pixel(depth, frame, px - bloomx, px + bloomx, py - bloomy, py + bloomy)
	return dat / (2 * constants.OSA)

def render_frame(frame):
	depth, frame = divmod(frame, constants.LOOP_LENGTH)

	scale_frame = constants.INIT_NO_SCALE if depth <= 0 and frame <= constants.INIT_NO_SCALE else frame
	scalex = constants.SCALE_A * math.exp(constants.SCALE_K * scale_frame)
	scaley = scalex * constants.HEIGHT / constants.WIDTH

	centrex, centrey = constants.CENTRES_FLOAT[depth]
	xmin = centrex - scalex/2
	ymin = centrey - scaley/2

	for y in range(constants.HEIGHT):
		#print(f"{y=}")
		for x in range(constants.WIDTH):
			yield render_pixel_osa(depth, frame,
				xmin + scalex * (x / constants.WIDTH),
				xmin + scalex * ((x + 1) / constants.WIDTH),
				ymin + scaley * (y / constants.HEIGHT),
				ymin + scaley * ((y + 1) / constants.HEIGHT))

	clear_cache()

def save_frame(frame, dat):
	with open(f"frames/{frame:08d}.pgm", "w") as fp:
		print("P2", file=fp)
		print(f"{constants.WIDTH} {constants.HEIGHT} 255", file=fp)
		for ix, x in enumerate(dat):
			print(int(x * 255), file=fp, end=" ")
			if (ix + 1) % constants.WIDTH == 0:
				print(file=fp)
	subprocess.check_call(["convert", f"frames/{frame:08d}.pgm", f"frames/{frame:08d}.png"])
	os.unlink(f"frames/{frame:08d}.pgm")

def doframe(frame):
	print(frame)
	dat = render_frame(frame)
	save_frame(frame, dat)

def main():
	for i in range(0, 5160, 20):
		doframe(i)
	#doframe(0)

def main_profile():
	import cProfile
	import time
	prof = cProfile.Profile()
	prof.runcall(main)
	prof.dump_stats(time.strftime("%Y%m%d-%H%M%S") + ".profile")

if __name__ == '__main__':
	main()
	#main_profile()
