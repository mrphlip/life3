#!/usr/bin/env golly
require "gplus.strict"
local g = golly()

local PERIOD = 35328

os.execute("rm -rf tiles/")

function dotileset (n)
	while g.numlayers() > 1 do
		g.dellayer()
	end
	g.new("make-tile-" .. n)

	for i = 0,8 do
		g.setcell(i % 3, i // 3, (n >> i) & 1)
	end
	g.select({0,0,3,3})
	g.open(g.getdir("app") .. "Scripts/Lua/metafier.lua")

	-- first step can have some fluff we don't want
	g.step()

	os.execute("mkdir -p tiles/" .. n)
	for i = 1,PERIOD do
		g.show("Tile " .. n .. " step " .. i)
		local cells = g.getcells({2048,2048,2048,2048})
		g.store(cells, "tiles/" .. n .. "/" .. (i-1) .. ".rle")
		g.step()
	end
end

for tilenum = 0,511 do
	dotileset(tilenum)
end

g.doevent("key q cmd") -- quit
