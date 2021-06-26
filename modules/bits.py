import sys

BITS_PER_SLOT = sys.int_info.bits_per_digit

class BitVector(object):
	def __init__(self, length_or_data):
		if isinstance(length_or_data, int):
			self.length = length
			self._data = [0] * ((length + BITS_PER_SLOT - 1) // BITS_PER_SLOT)
		else:
			self._data = list(self._build_init_data(length_or_data))

	def _build_init_data(self, data):
		length = 0
		pos = 0
		val = 0
		for bit in data:
			if bit:
				val |= (1 << pos)
			pos += 1
			if pos >= BITS_PER_SLOT:
				yield val
				length += pos
				val = pos = 0
		if pos >= 0:
			yield val
			length += pos
		self.length = length

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
		for i, dat in enumerate(self._data):
			for ix in range(min(BITS_PER_SLOT, self.length - BITS_PER_SLOT*i)):
				yield bool(dat & 1)
				dat >>= 1

	def __len__(self):
		return self.length

class BitGrid(BitVector):
	def __init__(self, width, height, data=None):
		if data is None:
			super().__init__(width * height)
		else:
			super().__init__(data)
			if self.length != width * height:
				raise ValueError("initialise data has wrong length")
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
