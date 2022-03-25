#!/bin/bash
set -e

# clean environment
rm -f constants.py constants.lua constants.h
rm -rf tiles/* tile_on.gz
rm -rf frames/

# generate data
./gen_constants.py
#./make_tiles_full.lua
./make_tiles_multiproc.sh

# generate animation
mkdir -p frames
make make_animation
./make_animation_multiproc.sh

# generate video file
./make_video.sh
