from __future__ import division

import golly as g
from math import floor, ceil, log
from os import system, unlink

resx, resy = 1920, 1080 # woo 1080p
osa = 3 # 3x3 oversampling
framerate = 30
#resx, resy = 160, 90
#osa = 2
#framerate = 5
framecount = framerate*90 # 90 seconds long seems reasonable
outputmask = "/home/phlip/lifeanim/%08d.%s" # outputmask % (frameno, extension)
cellsize = osa # make cells larger by a full pixel in each direction, to cut down on moire effects

centrex, centrey = 114500, 4365
initw, inith = 96, 54
finalscale = 11.0 # so that we scale out by a factor of 2**11 over the animation
finalratefact = 17.0  # so that we speed up by a factor of 2**17 over the animation (the metapixels animate at about 2**-15 of the speed)
initrate = 1 # initially approx one step per second
initrateadj = initrate * framecount/framerate/(finalratefact*log(2)) # magic calculation to make it so that d/dt of setframe(t) at 0 is initrate

curstep = 0
def setstep(n):
	global curstep
	n = int(round(n))
	if n < curstep:
		return
	g.run(n - curstep)
	curstep = n

def setframe(t):
	setstep(initrateadj * 2**(finalratefact * t))

class Rect:
	def __init__(self, l, t, w, h):
		self.left = l
		self.top = t
		self.width = w
		self.height = h

def calcscale(t):
	if t < 3*framerate/framecount:
		t = 3*framerate/framecount # don't zoom out for the first 3 seconds
	w = initw * 2**(finalscale * t)
	h = inith * 2**(finalscale * t)
	l = centrex - w / 2.0
	t = centrey - h / 2.0
	return Rect(l,t,w,h)

def clamp(x,minim,maxim):
	if x < minim:
		return minim
	if x > maxim:
		return maxim
	return x

def doframe(n):
	t = n/framecount
	setframe(t)
	sc = calcscale(t)
	# get all the cells in the view area
	cells = g.getcells([sc.left, sc.top, sc.width, sc.height])
	# generate a large image (for oversampling)
	output = [[0 for x in xrange(resx * osa)] for y in xrange(resy * osa)]
	# draw all the live cells on the image
	for i in xrange(0, len(cells), 2):
		cellx, celly = cells[i:i+2]
		# find the bounds of this cell on the screen
		xmin = int(floor(((cellx - sc.left) / sc.width) * resx * osa))
		xmax = int(floor(((cellx - sc.left + 1) / sc.width) * resx * osa)) + 1
		ymin = int(floor(((celly - sc.top) / sc.height) * resy * osa))
		ymax = int(floor(((celly - sc.top + 1) / sc.height) * resy * osa)) + 1
		# make the cells slightly larger and overlapping, to reduce the moire effects
		xmin -= cellsize
		ymin -= cellsize
		xmax += cellsize
		ymax += cellsize
		# draw the cell on the image
		xmin = clamp(xmin, 0, resx * osa)
		xmax = clamp(xmax, 0, resx * osa)
		ymin = clamp(ymin, 0, resy * osa)
		ymax = clamp(ymax, 0, resy * osa)
		for y in xrange(ymin, ymax):
			output[y][xmin:xmax] = [1] * (xmax - xmin)
	# Scale down the oversampled image to the target size, by averaging
	if osa > 1:
		output = [[sum(output[i][j] for i in xrange(y*osa,(y+1)*osa) for j in xrange(x*osa,(x+1)*osa)) for x in xrange(resx)] for y in xrange(resy)]
	# Save the image as a PGM, and then use ImageMagick to convert it to PNG
	with open(outputmask % (n, "pgm"), 'w') as fp:
		fp.write("P2\n%d %d\n%d\n" % (resx, resy, osa*osa))
		sc = calcscale(t)
		for row in output:
			fp.write(' '.join(map(str,row)))
			fp.write('\n')
	system("convert %s -depth 8 %s" % (outputmask % (n, "pgm"), outputmask % (n, "png")))
	unlink(outputmask % (n, "pgm"))

# Parameters so that I can run several instances of Golly and have them render separate slices of the frames
# and thus make use of my multicore CPU...
def main(step=1,start=0):
	global curstep
	g.reset()
	curstep = 0
	for i in xrange(start,framecount,step):
		g.show("Frame %d of %d..." % (i+1, framecount));
		doframe(i)

main()
# or, make copies of the script and have each copy have one of, eg:
#main(3,0)
#main(3,1)
#main(3,2)
# and then run three instances of Golly and have each run a different copy of the script
