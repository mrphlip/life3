#!/usr/bin/env python3
import gzip
import sys
import struct

filename = sys.argv[1]
with gzip.open(filename, "rb") as fpin:
	with open(filename + ".pbm", "wb") as fpout:
		width, height = struct.unpack("<LL", fpin.read(8))
		fpout.write(f"P4\n{width} {height}\n".encode("ascii"))
		for i in range(width*height//8):
			c, = fpin.read(1)
			c = (c & 0xF0) >> 4 | (c & 0x0F) << 4
			c = (c & 0xCC) >> 2 | (c & 0x33) << 2
			c = (c & 0xAA) >> 1 | (c & 0x55) << 1
			fpout.write(bytes([c]))
