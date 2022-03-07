#!/usr/bin/env golly
local make_tiles_core = require "make_tiles_core"

make_tiles_core.frames = {0,8}

make_tiles_core.dotileset(0)
make_tiles_core.dotileset(16)
make_tiles_core.dotileset(57)
make_tiles_core.dotileset(511)

make_tiles_core.quit()
