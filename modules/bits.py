import sys

BITS_PER_SLOT = sys.int_info.bits_per_digit

class BitVector(object):
	def __init__(self, length):
		self.length = length
		self._data = [0] * ((length + BITS_PER_SLOT - 1) // BITS_PER_SLOT)

	def _getslot(self, ix):
		if ix >= self.length or ix < -self.length:
			raise IndexError("index out of range")
		if ix < 0:
			ix += self.length
		return ix // BITS_PER_SLOT, 1 << (ix % BITS_PER_SLOT)

	def __getitem__(self, ix):
		slot, val = self._getslot(ix)
		return bool(self._data[slot] & val)

	def __setitem__(self, ix, newval):
		slot, val = self._getslot(ix)
		if newval:
			self._data[slot] |= val
		else:
			self._data[slot] &= ~val

	def __iter__(self):
		for i in range(self.length):
			yield self[i]

	def __len__(self):
		return self.length

class BitGrid(BitVector):
	def __init__(self, width, height):
		super().__init__(width * height)
		self.width = width
		self.height = height

	def __getitem__(self, ix):
		if isinstance(ix, tuple):
			x, y = ix
			ix = x + y * self.width
		return super().__getitem__(ix)

	def __setitem__(self, ix, newval):
		if isinstance(ix, tuple):
			x, y = ix
			ix = x + y * self.width
		return super().__setitem__(ix, newval)
