#ifndef __BITGRID_H__
#define __BITGRID_H__

const int BITS_PER_SLOT = 64;

class BitGrid {
public:
	const int width, height;
	const uint64_t * const data;

private:
	BitGrid(int width, int height, uint64_t *data)
		: width(width), height(height), data(data)
	{}
public:
	~BitGrid() {
		delete[] this->data;
	}

	static BitGrid * load(std::string filename);

	bool get(int ix) {
		int slot = ix / BITS_PER_SLOT, pos = ix % BITS_PER_SLOT;
		return bool(this->data[slot] & (1ull << pos));
	}
	bool get(int x, int y) {
		return this->get(x + y * this->width);
	}

	int context(int ix) {
		int slot = ix / BITS_PER_SLOT, pos = ix % BITS_PER_SLOT;
		if (pos == 0) {
			// need context from previous slot
			return (this->data[slot - 1]) >> (BITS_PER_SLOT - 1) | (this->data[slot] & 0x3) << 1;
		} else if (pos == BITS_PER_SLOT - 1) {
			// need context from the following slot
			return (this->data[slot] >> (BITS_PER_SLOT - 2)) | (this->data[slot + 1] & 0x1) << 2;
		} else {
			// everything is in one slot
			return (this->data[slot] >> (pos - 1)) & 0x7;
		}
	}
	int context(int x, int y) {
		int ix = x + y * this->width;
		int above = this->context(ix - this->width), here = this->context(ix), below = this->context(ix + this->height);
		return above | here<<3 | below<<6;
	}

	bool is_covered(int ix1, int ix2) {
		int slot1 = ix1 / BITS_PER_SLOT, pos1 = ix1 % BITS_PER_SLOT;
		int slot2 = ix2 / BITS_PER_SLOT, pos2 = ix2 % BITS_PER_SLOT;

		if (slot1 == slot2) {
			return bool(this->data[slot1] & ((1ull << pos2) - (1ull << pos1)));
		}

		if (this->data[slot1] >> pos1)
			return 1;
		for (int i = slot1 + 1; i < slot2; i++)
			if (this->data[i])
				return 1;
		if (pos2 > 0 && this->data[slot2] & ((1ull << pos2) - 1))
			return 1;
		return 0;
	}
	bool is_covered(int x1, int x2, int y1, int y2) {
		int ixstart = x1 + y1 * this->width;
		int ixend = x1 + y2 * this->width;
		int w = x2 - x1;
		for (int ix = ixstart; ix < ixend; ix += this->width)
			if (this->is_covered(ix, ix + w))
				return 1;
		return 0;
	}

private:
	BitGrid(BitGrid&);
	BitGrid& operator=(BitGrid&);
};

#endif
