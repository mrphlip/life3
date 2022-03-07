#!/bin/bash
set -e

# be a little nice - keep one core free
NPROC=$(nproc --ignore 1)

for I in {1..$NPROC}
do
	(
		echo '#!/usr/bin/env golly'
		echo 'local make_tiles_core = require "make_tiles_core"'
		echo "make_tiles_core.dofullset($I, $NPROC)"
		echo 'make_tiles_core.quit()'
	) > make_tiles_$I.lua
	chmod +x make_tiles_$I.lua
	./make_tiles_$I.lua
done

wait
