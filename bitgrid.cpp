#include <cstdint>
#include <string>
#include <iostream>
#include <fstream>
#include <cstring>
#include <zlib.h>
#define ENABLE_ZLIB_GZIP 32

#include "bitgrid.h"

void die(std::string message) {
	// Proper error handling is for real projects
	std::cerr << message << std::endl;
	std::exit(1);
}

BitGrid * BitGrid::load(std::string filename) {
	// yayyy zlib
	uint32_t width, height;
	uint64_t *data = NULL;
	unsigned char *dataptr = NULL;
	int datalen;

	// initialise file
	std::ifstream fp;
	fp.exceptions(std::ifstream::eofbit | std::ifstream::failbit | std::ifstream::badbit);
	fp.open(filename, std::ifstream::binary);
	fp.seekg(0, fp.end);
	int ziplen = fp.tellg();
	fp.seekg(0, fp.beg);

	// initialise zlib
	const int BUFLEN = 4096;
	unsigned char inbuffer[BUFLEN], outbuffer[BUFLEN];
	z_stream strm;
	memset(&strm, 0, sizeof(strm));
	strm.zalloc = Z_NULL;
	strm.zfree = Z_NULL;
	strm.opaque = Z_NULL;
	strm.next_in = inbuffer;
	strm.avail_in = 0;
	if (inflateInit2(&strm, 15|ENABLE_ZLIB_GZIP) < 0)
		die("Error initialising zlib");

	while (ziplen > 0) {
		// read a chunk of data from the file
		int chunklen = ziplen > BUFLEN ? BUFLEN : ziplen;
		fp.read(reinterpret_cast<char*>(inbuffer), chunklen);
		if (!fp) die("Error reading from " + filename);
		strm.next_in = inbuffer;
		strm.avail_in = chunklen;
		ziplen -= chunklen;

		// decompress the chunk
		do {
			strm.avail_out = BUFLEN;
			strm.next_out = outbuffer;
			if (inflate(&strm, Z_NO_FLUSH) < 0)
				die("Gzip error in " + filename);
			int avail_data = BUFLEN - strm.avail_out;

			// is this the very beginning of the file?
			// read the header
			int dataoffset = 0;
			if (!data) {
				if (avail_data < 8)
					die("Didn't read enough data in the first chunk somehow, for " + filename);
				std::memcpy(&width, outbuffer, 4);
				std::memcpy(&height, outbuffer + 4, 4);
				// figure out how big the data buffer needs to be
				int len = width * height;
				int slots = len / BITS_PER_SLOT;
				if (len % BITS_PER_SLOT > 0)
					slots++;
				data = new uint64_t[slots];
				dataptr = reinterpret_cast<unsigned char*>(data);
				datalen = slots * 8;

				dataoffset = 8;
			}

			// read the body of the data
			if (avail_data - dataoffset > datalen)
				die("Too much data in " + filename);
			memcpy(dataptr, outbuffer + dataoffset, avail_data - dataoffset);
			dataptr += avail_data - dataoffset;
			datalen -= avail_data - dataoffset;
		} while (strm.avail_out == 0);
	}

	fp.close();
	inflateEnd(&strm);

	if (datalen > 0)
		die("Not enough data in " + filename);

	return new BitGrid(width, height, data);
}
