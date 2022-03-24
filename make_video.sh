#!/bin/bash
set -e
ARGS=(
	-pattern_type glob -f image2 -r 60 -i 'frames/*/*.png'
)
if [ -f soundtrack.m4a ]
then
	ARGS+=(-i soundtrack.m4a)
fi
ARGS+=(
	-codec:v libx264 -b:v 60M -profile:v high -pix_fmt yuv420p
	-codec:a copy
	-movflags +faststart
	life.mp4
)
ffmpeg "${ARGS[@]}"
