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
			width = int(match.group(1))
			height = int(match.group(2))
			break
	else:
		raise ValueError("Did not find header - file blank?")

	return BitGrid(width, height, _rle_decode(fp, width))

_unsupported = set("BCDEFGHIJKLMNOPQRSTUVWXYZpqy")
_supported = {'.': 0, 'b': 0, 'A': 1, 'o': 1}
def _rle_decode(fp, width):
	repeat = ''
	xpos = 0
	for line in fp:
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
					repeatint = int(repeat)
					yield from [ch] * repeatint
					xpos += repeatint
					repeat = ''
				else:
					yield ch
					xpos += 1
			elif ch == '$':
				if repeat:
					repeatint = int(repeat)
					yield from [False] * (repeatint * width - xpos)
					repeat = ''
				else:
					yield from [False] * (width - xpos)
				xpos = 0
			elif ch == '!':
				yield from [False] * (width - xpos)
				return
			else:
				raise ValueError("Unrecognised character: %r" % ch)
