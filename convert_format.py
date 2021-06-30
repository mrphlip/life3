#!/usr/bin/env python3
import sys
import os
from modules import rle
import gzip

def main(basename):
	with open(basename + ".rle", "r") as fp:
		tile = rle.rle_read(fp)
	with gzip.open(basename + ".gz", "wb") as fp:
		tile.dump(fp)
	os.unlink(basename + ".rle")

if __name__ == '__main__':
	main(sys.argv[1])
