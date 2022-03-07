local make_tiles_core = {}

require "gplus.strict"
local g = golly()

make_tiles_core.frames = {0}
make_tiles_core.frame_offset = 1
local status, constants = pcall(require, "constants")
if (status) then
	make_tiles_core.frames = constants.FRAMES
	make_tiles_core.frame_offset = constants.FRAME_OFFSET
end

--os.execute("rm -rf tiles/")

function make_tiles_core.dotileset (n)
	while g.numlayers() > 1 do
		g.dellayer()
	end
	g.new("make-tile-" .. n)

	for i = 0,8 do
		g.setcell(i % 3, i // 3, (n >> i) & 1)
	end
	g.select({0,0,3,3})
	g.open(g.getdir("app") .. "Scripts/Lua/metafier.lua")

	g.run(make_tiles_core.frame_offset)

	os.execute("mkdir -p tiles/" .. n)
	local laststep = 0
	for i = 1,#make_tiles_core.frames do
		local step = make_tiles_core.frames[i]
		if (step > laststep) then
			g.run(step - laststep)
			laststep = step
		end
		g.show("Tile " .. n .. " step " .. i .. "/" .. #make_tiles_core.frames)
		local cells = g.getcells({2048,2048,2048,2048})
		local basename = "tiles/" .. n .. "/" .. step
		g.store(cells, basename .. ".rle")
		os.execute("./convert_format.py " .. basename)
	end
end

function make_tiles_core.dofullset (ix, n)
	-- Generate a slice of the tilesets
	-- can call, eg, dofullset(1, 3), dofullset(2, 3), dofullset(3, 3)
	-- in separate processes, to make use of multiple CPU cores
	for tilenum = (ix-1),511,n do
		make_tiles_core.dotileset(tilenum)
	end
end

function make_tiles_core.quit()
	g.doevent("key q cmd")
end

return make_tiles_core
