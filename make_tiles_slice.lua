#!/usr/bin/env golly
local make_tiles_core = require "make_tiles_core"

make_tiles_core.dotileset(16)
make_tiles_core.dotileset(7)

make_tiles_core.frames = {0}
make_tiles_core.dofullset(1, 1)

make_tiles_core.quit()
