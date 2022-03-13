#include <iostream>
#include <fstream>
#include <iomanip>
#include <map>
#include <sstream>
#include <cmath>
#include <cstdlib>
#include <cstdio>
#include <ctime>
#include <unistd.h>
#include <sys/stat.h>

#include "bitgrid.h"
#include "constants.h"

std::map<std::pair<int, int>, BitGrid*> tilecache;
BitGrid &get_tile(int context, int frame) {
	std::pair<int,int> key = std::make_pair(context, frame);
	auto i = tilecache.find(key);
	if (i != tilecache.end())
		return *i->second;

	std::ostringstream filename;
	filename << "tiles/" << context << "/" << frame << ".gz";
	BitGrid *bg = BitGrid::load(filename.str());
	tilecache[key] = bg;
	return *bg;
}
void clear_tilecache() {
	for (auto i = tilecache.begin(); i != tilecache.end(); i++) {
		delete i->second;
	}
	tilecache.clear();
}

int ifloor(double);
int iceil(double);
int ifloor(double x) {
	if (x < 0)
		return -iceil(-x);
	return int(x);
}
int iceil(double x) {
	if (x < 0)
		return -ifloor(-x);
	int i = int(x);
	if (x > double(i))
		i++;
	return i;
}

bool is_covered(int depth, int frame, int depthofs, int depthmax, double x1, double x2, double y1, double y2, int context) {
	int frameix;
	if (depthofs >= 2) {
		frameix = 0;
	} else {
		frameix = frame + LOOP_LENGTH * (1 - depthofs);
	}
	BitGrid &tile = get_tile(context, FRAMES[frameix]);
	if (depthofs <= depthmax) {
		return tile.is_covered(ifloor(x1), iceil(x2), ifloor(y1), iceil(y2));
	} else {
		int ix1 = ifloor(x1), ix2 = ifloor(x2), iy1 = ifloor(y1), iy2 = ifloor(y2);
		double newx1 = (x1 - ix1) * LOOP_SCALE, newx2 = (x2 - ix2) * LOOP_SCALE, newy1 = (y1 - iy1) * LOOP_SCALE, newy2 = (y2 - iy2) * LOOP_SCALE;
		if (ix2 > ix1 + 1 || iy2 > iy1 + 1) {
			// shouldn't happen, sanity check shortcut
			return 1;
		}
		if (ix1 == ix2 && iy1 == iy2) {
			return is_covered(depth, frame, depthofs - 1, depthmax, newx1, newx2, newy1, newy2, tile.context(ix1, iy1));
		} else if (ix1 == ix2) {
			return (
				is_covered(depth, frame, depthofs - 1, depthmax, newx1, newx2, newy1, LOOP_SCALE, tile.context(ix1, iy1)) ||
				is_covered(depth, frame, depthofs - 1, depthmax, newx1, newx2, 0, newy2, tile.context(ix1, iy2))
			);
		} else if (iy1 == iy2) {
			return (
				is_covered(depth, frame, depthofs - 1, depthmax, newx1, LOOP_SCALE, newy1, newy2, tile.context(ix1, iy1)) ||
				is_covered(depth, frame, depthofs - 1, depthmax, 0, newx2, newy1, newy2, tile.context(ix2, iy1))
			);
		} else {
			return (
				is_covered(depth, frame, depthofs - 1, depthmax, newx1, LOOP_SCALE, newy1, LOOP_SCALE, tile.context(ix1, iy1)) ||
				is_covered(depth, frame, depthofs - 1, depthmax, 0, newx2, newy1, LOOP_SCALE, tile.context(ix2, iy1)) ||
				is_covered(depth, frame, depthofs - 1, depthmax, newx1, LOOP_SCALE, 0, newy2, tile.context(ix1, iy2)) ||
				is_covered(depth, frame, depthofs - 1, depthmax, 0, newx2, 0, newy2, tile.context(ix2, iy2))
			);
		}
	}
}

unsigned char render_pixel_level(int depth, int frame, int depthmax, double x1, double x2, double y1, double y2) {
	x1 = CENTRESX[depth] + x1 / LOOP_SCALE;
	x2 = CENTRESX[depth] + x2 / LOOP_SCALE;
	y1 = CENTRESY[depth] + y1 / LOOP_SCALE;
	y2 = CENTRESY[depth] + y2 / LOOP_SCALE;

	x1 = CENTRESX[depth+1] + x1 / LOOP_SCALE;
	x2 = CENTRESX[depth+1] + x2 / LOOP_SCALE;
	y1 = CENTRESY[depth+1] + y1 / LOOP_SCALE;
	y2 = CENTRESY[depth+1] + y2 / LOOP_SCALE;

	return is_covered(depth, frame, 2, depthmax, x1, x2, y1, y2, TOPLEVEL_CONTEXT) ? 255 : 0;
}

unsigned char render_pixel(int depth, int frame, double x1, double x2, double y1, double y2) {
	if (depth >= 1 && frame < INIT_NO_SCALE) {
		int p0 = render_pixel_level(depth, frame, 0, x1, x2, y1, y2);
		int p1 = render_pixel_level(depth, frame, -1, x1, x2, y1, y2);
		return (p1 * (INIT_NO_SCALE - frame) + p0 * frame) / INIT_NO_SCALE;
	} else {
		return render_pixel_level(depth, frame, 0, x1, x2, y1, y2);
	}
}

unsigned char render_pixel_osa(int depth, int frame, double x1, double x2, double y1, double y2) {
	double dx = (x2 - x1) / 2;
	double dy = (y2 - y1) / 2;
	double cx = (x1 + x2) / 2;
	double cy = (y1 + y2) / 2;
	double bloomx = dx * BLOOM;
	double bloomy = dy * BLOOM;
	if (OSA > 1) {
		// do over-sampling
		int dat = 0;
		for (int i = 0; i < OSA; i++) {
			double factor = 1.0 + double(i) / OSA;
			dat += render_pixel(depth, frame, cx - bloomx * factor, cx + bloomx * factor, cy - bloomy * factor, cy + bloomy * factor);
		}
		return dat / OSA;
	} else {
		// single-sample
		return render_pixel(depth, frame, cx - bloomx, cx + bloomx, cy - bloomy, cy + bloomy);
	}
}

unsigned char *render_frame(int frame) {
	int depth = frame / LOOP_LENGTH;
	frame = frame % LOOP_LENGTH;

	int scale_frame = depth <= 0 && frame < INIT_NO_SCALE ? INIT_NO_SCALE : frame;
	double scalex = SCALE_A * std::exp(SCALE_K * scale_frame);
	double scaley = scalex * HEIGHT / WIDTH;

	double xmin = CENTRES_FLOATX[depth] - scalex/2;
	double ymin = CENTRES_FLOATY[depth] - scaley/2;

	static unsigned char image_buffer[WIDTH * HEIGHT];
	unsigned char *ptr = image_buffer;

	for (int y = 0; y < HEIGHT; y++)
		for (int x = 0; x < WIDTH; x++)
			*ptr++ = render_pixel_osa(depth, frame, xmin + scalex * double(x)/WIDTH, xmin + scalex * double(x+1)/WIDTH, ymin + scaley * double(y)/HEIGHT, ymin + scaley * double(y+1)/HEIGHT);

	clear_tilecache();

	return image_buffer;
}

void save_frame(int frame, unsigned char *image) {
	std::ostringstream filename;
	filename << "frames/" << std::setw(4) << std::setfill('0') << (frame / LOOP_LENGTH);
	if (access(filename.str().c_str(), F_OK)) {
		if (mkdir(filename.str().c_str(), 0755)) {
			std::cerr << "Error creating subdir" << std::endl;
			std::exit(1);
		}
	}
	filename << '/' << std::setw(8) << std::setfill('0') << frame;
	std::string pgmfilename = filename.str() + ".pgm";
	std::string pngfilename = filename.str() + ".png";

	std::ofstream fp;
	fp.exceptions(std::ofstream::failbit | std::ofstream::badbit);
	fp.open(pgmfilename);

	fp << "P2\n" << WIDTH << " " << HEIGHT << " 255\n";
	unsigned char *ptr = image;
	for (int y = 0; y < HEIGHT; y++) {
		for (int x = 0; x < WIDTH; x++) {
			fp << int(*ptr++) << " ";
		}
		fp << "\n";
	}
	fp.close();

	std::ostringstream cmdline;
	cmdline << "convert " << pgmfilename << " " << pngfilename;
	if (std::system(cmdline.str().c_str())) {
		std::cerr << "Error running convert" << std::endl;
		std::exit(1);
	}
	if (std::remove(pgmfilename.c_str())) {
		std::cerr << "Error unlinking pgm file" << std::endl;
		std::exit(1);
	}
}

void doframe(int frame) {
	std::time_t now = time(NULL);
	std::string nowstr = std::ctime(&now);
	size_t pos = nowstr.find_last_not_of('\n');
	if (pos == std::string::npos)
		nowstr = "";
	else if (pos < nowstr.length() - 1)
		nowstr.erase(pos + 1, std::string::npos);

	std::cout << frame << " - " << nowstr << std::endl;

	unsigned char *image = render_frame(frame);
	save_frame(frame, image);
}

void doanim(int ofs, int step) {
	for (int i = ofs; i < LOOP_LENGTH * LOOP_COUNT; i += step) {
		doframe(i);
	}
}

void usage() {
	std::cout
		<< "Usage:\n"
		<< "  make_animation              - render entire animation\n"
		<< "  make_animation frame        - render a single frame\n"
		<< "  make_animation offset step  - render a slice of the animation\n";
}

int main(int argn, char **argv) {
	if (argn == 1) {
		doanim(1, 1);
	} else if (argn == 2) {
		char *endptr;
		int frame = std::strtol(argv[1], &endptr, 0);
		if (*endptr != '\0') {
			usage();
			return 1;
		}

		doframe(frame);
	} else if (argn == 3) {
		char *endptr;
		int ofs = std::strtol(argv[1], &endptr, 0);
		if (*endptr != '\0') {
			usage();
			return 1;
		}
		int step = std::strtol(argv[2], &endptr, 0);
		if (*endptr != '\0') {
			usage();
			return 1;
		}

		doanim(ofs, step);
	} else {
		usage();
	}

	return 0;
}
