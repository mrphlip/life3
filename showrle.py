#!/usr/bin/env python3

from modules import rle
import sys
import cProfile

def main(fn):
	print("reading")
	with open(fn) as fp:
		grid = rle.rle_read(fp)
	print("writing")
	with open(fn + ".pbm", "w") as fp:
		print("P1", file=fp)
		print(f"{grid.width} {grid.height}", file=fp)
		for i in grid:
			fp.write("1 " if i else "0 ")
		print(file=fp)
	print("done")

def do_profile(fn):
	prof = cProfile.Profile()
	prof.runcall(main, fn)
	prof.dump_stats("showrle.profile")

if __name__ == '__main__':
	#main(sys.argv[1])
	do_profile(sys.argv[1])
