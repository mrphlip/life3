# Life in Life in Life generator
This is the code that was used to generate the [Life in Life in Life video](https://youtu.be/4lO0iZDzzXk).

This uses the [OTCA Metapixel](http://otcametapixel.blogspot.com/) to generate an animation of Conway's Game of Life, simulated within Conway's Game of Life, nested multiple times.

The code here is a bit scattered around, but can be mostly be broken up as:
1. Lua scripts to run Golly to simulate the Metapixel and extract the results as tiles, which will be stitched together to form the video.
    * `make_tiles_core.lua`
    * `make_tiles_{basic,slice,full}.lua`
    * `make_tiles_multiproc.sh`
    * `convert_format.py`
    * `modules/rle.py`
1. C++ code to stitch those tiles together and render the final video frames
    * `make_animation.cpp`
    * `bitgrid.cpp`/`.h`
    * `Makefile`
    * `make_animation_multiproc.sh`
1. Python code that is an earlier version of the same rendering code, from before I realised that Python is not a great language to do this sort of intensive number-crunching and bit-manipulation stuff, and ported it to C++, improving the runtime by a factor of 80(!).
    * `make_animation.py`
    * `modules/bits.py`
1. Code to generate a pre-prepare a bunch of settings and constants, which controls things like how big the video is, how fast it zooms out, what point in the cell it zooms out from in each layer, etc.
    * `constants_in.py`
    * `gen_constants.py`
1. Other assorted miscellaneous scripts:
    * `make_video.sh` &ndash; convert the final video to MP4 to upload
    * `build.sh` &ndash; run all everything in order... more intended as reference, than to actually be run directly
    * `show_tile.py` &ndash; convert the tile data into an image format so it can be easily inspected
    * `showrle.py` &ndash; convert the RLE file format exported from Golly into an image format

## How to run the code
On the offchance you actually want to run this code yourself, rather than just reading it out of curiosity, here's what you would need to do:
### Prerequisites
* Linux &ndash; this could probably be converted to work on Windows but that's what it's written for
* Golly (including Lua engine)
* Python 3
* GCC, make, and whatever other packages your distro needs to build C++ code
* zlib
* ImageMagick
* FFmpeg
### Running
In theory, you could just run `build.sh` and it would do everything. But chances are that would take much too long, and you'd probably want to run each of the stages individually. So the build script mostly exists as a reference, so you can open it and see what the steps are, in what order.
### Setting config
To start with, you'll want to set up some settings to configure how you want the video to come out. Resolution, FPS, that sort of thing. But also some other settings, like how fast it zooms out, or how many levels of nesting to animate. And some more specific settings, like what point it should zoom out from at each level.

Edit the file `constants_in.py`, there are comments in the file to explain what the settings do.

Once this is done, run `./gen_constants.py`, this will generate constants files for the different components.
### Generating tiles
The next step is to run Golly, to generate images of how each metapixel looks like in different contexts, and how it evolves over time.

If you have Golly installed and in your search path, you should simply be able to run `./make_tiles_full.lua`, which will invoke Golly, generate all the tiles, and then quit when it is done. Just don't click anything in the Golly window while the script is running.

If you're feeling very fancy, you can run `./make_tiles_multiproc.sh`, which will spawn multiple instances of Golly in order to make use of multiple CPU cores (as Golly appears to be single-threaded, each instance of Golly will only use a single CPU core), which will significantly speed up generation, at the cost of having multiple Golly windows that you need to remember not to click on until they're done.

The output of this will be a directory called `tiles/` which contains a ton of little data files, each one of which contains a representation of what a metacell looks like in a specific context, after a certain amount of time.

Fair warning: this step of the process took a week to run on my computer, and generated 40GB of data, so make sure you have the time and space to spare.
### Generating video
The final big step is generating the actual video frames, based on the tiles.

To do this, run `make` to build the code, and then `./make_animation` to kick it off.

Again, if you're feeling fancy, you can run `./make_animation_multiproc.sh` to run multiple processes to make use of multiple CPU cores.

The output of this will be a directory called `frames/` which contains a sequence of PNG images, which is the final animation for the video.
### Building video file
The final step is to run `./make_video.sh` which will use FFmpeg to convert the image sequence into an actual MP4 file, which can then be uploaded to YouTube or wherever. If you have a `soundtrack.m4a` file, it will also mix that into the final video. You may want to edit the `make_video.sh` file first and twiddle with the settings, in particular the bitrate... the bitrate that's in there is intended for 4K video, so if you're rendering at a lower resolution you will probably want to lower the bitrate to match.
