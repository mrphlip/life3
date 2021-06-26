from .bits import BitGrid
from io import StringIO
import re

_re_header = re.compile(r"^\s*x\s*=\s*(\d*)\s*,\s*y\s*=\s*(\d*)\s*,\s*rule\s*=\s*[^,]*\s*$", re.IGNORECASE)

def rle_read(fp):
	if isinstance(fp, str):
		fp = StringIO(fp)

	grid = None
	x = y = 0
	for line in fp:
		line = line.strip()
		if line[0] == '#' or not line:
			continue

		if grid is None:
			match = _re_header.match(line)
			if not match:
				raise ValueError("Could not parse header line: %r" % line)
			grid = BitGrid(int(match.group(1)), int(match.group(2)))
			continue

		for val in _rle_decode(line):
			if val == -1:
				x = 0
				y += 1
			else:
				grid[x, y] = val
				x += 1
	return grid

_unsupported = set("BCDEFGHIJKLMNOPQRSTUVWXYZpqy")
_supported = {'.': 0, 'b': 0, 'A': 1, 'o': 1, '$': -1}
def _rle_decode(line):
	repeat = ''
	for ch in line:
		if ch.isspace():
			pass
		elif ch.isdigit():
			repeat += ch
		elif ch in _unsupported:
			raise NotImplementedError("Multistate grids are not currently supported")
		elif ch in _supported:
			ch = _supported[ch]
			if repeat:
				for i in range(int(repeat)):
					yield ch
				repeat = ''
			else:
				yield ch
		elif ch == '!':
			return
		else:
			raise ValueError("Unrecognised character: %r" % ch)
