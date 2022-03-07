#!/bin/bash
set -e

NPROCS="$(($(ncpus) - 1))"

# clean environment
rm -f constants.py constants.lua
rm -rf tiles/* tile_on.gz
rm -rf frames/

# generate some basic tiles, for gen_constants
./make_tiles_basic.lua
cp tiles/16/0.gz tile_on.gz

# generate data
./gen_constants.py
#./make_tiles_full.lua
./make_tiles_multiproc.sh

# generate animation
mkdir -p frames
./make_animation.py
