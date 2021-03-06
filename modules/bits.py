import struct

BITS_PER_SLOT = 64

class BitVector(object):
	def __init__(self, length_or_data, rawdata=None):
		if rawdata is not None:
			if len(rawdata) != ((length_or_data + BITS_PER_SLOT - 1) // BITS_PER_SLOT):
				raise ValueError("Raw data not correct length")
			self.length = length_or_data
			self._data = rawdata
		elif isinstance(length_or_data, int):
			self.length = length_or_data
			self._data = [0] * ((length_or_data + BITS_PER_SLOT - 1) // BITS_PER_SLOT)
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
		if pos > 0:
			yield val
			length += pos
		self.length = length

	def _getslot(self, ix):
		if ix >= self.length or ix < -self.length:
			raise IndexError("index out of range")
		if ix < 0:
			ix += self.length
		slot, pos = divmod(ix, BITS_PER_SLOT)
		return slot, 1 << pos

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

	def __eq__(self, other):
		return self.length == other.length and self._data == other._data

	def context(self, ix):
		if ix >= self.length - 1 or ix < 1:
			raise IndexError("index out of range")
		slot, pos = divmod(ix, BITS_PER_SLOT)
		if pos == 0:
			return self._data[slot - 1] >> (BITS_PER_SLOT - 1) | (self._data[slot] & 0x03) << 1
		elif pos == BITS_PER_SLOT - 1:
			return self._data[slot] >> (BITS_PER_SLOT - 2) | (self._data[slot + 1] & 0x01) << 2
		else:
			return (self._data[slot] >> (pos - 1)) & 0x07

	def is_covered(self, start, end):
		startslot, startpos = divmod(start, BITS_PER_SLOT)
		endslot, endpos = divmod(end, BITS_PER_SLOT)

		if startslot == endslot:
			return bool(self._data[startslot] & ((1 << endpos) - (1 << startpos)))

		if self._data[startslot] >> startpos:
			return True
		if any(self._data[startslot + 1:endslot]):
			return True
		if endpos > 0 and self._data[endslot] & ((1 << endpos) - 1):
			return True
		return False

	def _dumpdata(self, fp):
		for i in range(0, len(self._data), 1024):
			chunk = self._data[i:i+1024]
			fp.write(struct.pack(f"<{len(chunk)}Q", *chunk))

	def dump(self, fp):
		fp.write(struct.pack("<L", self.length))
		self._dumpdata(fp)

	@classmethod
	def _loaddata(cls, fp):
		data = []
		buffer = b''
		while True:
			chunk = fp.read(4096)
			if not chunk:
				break

			# just in case it didn't actually read a multiple of 8 bytes somehow
			if buffer:
				chunk = buffer + chunk
			if len(chunk) % 8:
				cutoff = len(chunk) - len(chunk) % 8
				buffer = chunk[cutoff:]
				chunk = chunk[:cutoff]
			else:
				buffer = b''

			data.extend(struct.unpack(f"<{len(chunk)//8}Q", chunk))
		return data

	@classmethod
	def load(cls, fp):
		length, = struct.unpack("<L", fp.read(4))
		data = cls._loaddata(fp)
		return cls(length, rawdata=data)

class BitGrid(BitVector):
	def __init__(self, width, height, data=None, rawdata=None):
		if rawdata is not None:
			super().__init__(width * height, rawdata=rawdata)
		elif data is not None:
			super().__init__(data)
			if self.length != width * height:
				raise ValueError("initialise data has wrong length")
		else:
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

	def __eq__(self, other):
		return self.width == other.width and self.height == other.height and self._data == other._data

	def context(self, ix):
		if isinstance(ix, tuple):
			x, y = ix
			ix = x + y * self.width
		return super().context(ix - self.height) | super().context(ix) << 3 | super().context(ix + self.height) << 6

	def is_covered(self, start, end):
		startx, starty = start
		endx, endy = end
		ix = startx + starty * self.width
		endix = startx + endy * self.width
		dx = endx - startx
		while ix < endix:
			if super().is_covered(ix, ix + dx):
				return True
			ix += self.width
		return False

	def dump(self, fp):
		fp.write(struct.pack("<LL", self.width, self.height))
		self._dumpdata(fp)

	@classmethod
	def load(cls, fp):
		width, height = struct.unpack("<LL", fp.read(8))
		data = cls._loaddata(fp)
		return cls(width, height, rawdata=data)
