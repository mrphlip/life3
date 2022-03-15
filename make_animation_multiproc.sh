#!/bin/bash
set -e

# be a little nice - keep one core free
NPROC=$(nproc --ignore 1)

trap 'killall make_animation' INT

for I in $(seq 0 $((NPROC-1)) )
do
	./make_animation $I $NPROC &
done

wait
