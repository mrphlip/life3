#!/usr/bin/python
from __future__ import division
import sys, os
from math import cos, pi
twopi = 2.0 * pi # a much more useful constant - http://tauday.com/tau-manifesto

srate = 48000
length = 90
numsamples = srate * length

numchannels = 7
channeltheta = [0.0] * numchannels
def gensample(freqamps): # freqamps is [(channel 0 frequency, channel 0 amplitude), (chan 1 freq, chan 1 amp), ...]
	sample = 0.0
	for i in xrange(numchannels):
		channeltheta[i] += freqamps[i][0] / srate
		channeltheta[i] %= 1.0
		
		sample += freqamps[i][1] * cos(channeltheta[i] * twopi)
	return sample

basefreq = 25.0
def genfreqamp(n, chan):
	x = n / srate
	
	if x < 3: # ramp in for first 3 seconds
		x = x ** 2 / 6 + 1.5 # so that the value and first derivative are equal at the cutover
	
	if x >= length - 5 and x < length - 2: # ramp out for last 5 seconds
		x = length - 2 - 1.5 - (length - 2 - x) ** 2 / 6
	if x >= length - 2:
		x = length - 2 - 1.5
	
	x /= 10.0
	x += chan
	x %= float(numchannels)
	
	freq = basefreq * (2 ** x)
	amp = 1 - cos(x / numchannels * twopi) # ranges from 0 at min frequency, up to 2, down to 0 at max frequency
	return (freq, amp)

def main():
	samples = []
	maxsample = 0.0
	
	for i in xrange(numsamples):
		if i % srate == 0:
			print "\rGenerating: %3.0f%%" % (i / numsamples * 100.0),
			sys.stdout.flush()
		freqamps = [genfreqamp(i, c) for c in xrange(numchannels)]
		samples.append(gensample(freqamps))
		if abs(samples[-1]) > maxsample:
			maxsample = abs(samples[-1])
	print "\rGenerating: 100%   "
	sys.stdout.flush()
	
	# Generate the audio as a raw output file, and then use SoX to convert it to WAV
	with open("out.raw", "wb") as fp:
		for i,x in enumerate(samples):
			if i % srate == 0:
				print "\rWriting: %3.0f%%" % (i / numsamples * 100.0),
			sys.stdout.flush()
			n = int(round(x / maxsample * 32767))
			if n < 0:
				n += 65536
			fp.write(chr(n % 256) + chr(n // 256))
	print "\rWriting: 100%   "
	sys.stdout.flush()
	os.system("sox -t raw -r %d -b 16 -c 1 -e signed-integer --endian little out.raw out.wav" % (srate))
	os.unlink("out.raw")

main()