# Life in Life generator
This is the code that was used to generate the original [Life in Life video](https://youtu.be/xP5-iIeKXE8).

This uses the [OTCA Metapixel](http://otcametapixel.blogspot.com/) to generate an animation of Conway's Game of Life, simulated within Conway's Game of Life, nested multiple times.

This code is 10 years old at this point, and hasn't been updated since... it's just included here for reference, and to move the code into Github (rather than it just living in a random pastebin link).

You can tell it's old because
1. It's a Golly script written in Python 2 (Ubuntu removed Golly's Python scripting modules from their build because they wanted to remove everything with a Python2 dependency)
1. The encoding script uses `mencoder` to encode the video, when MPlayer has been obsolete for a long time. The newer iteration of the script uses FFmpeg instead.

The files here are:
* `lifeanim.py` &ndash; the main script, rendering images directly from Golly
* `soundgen.py` &ndash; generates a Shepard tone soundfile, the soundtrack of the [real original version of the video](https://youtu.be/zOwFvytK5K0) before I came to my senses and replaced the soundrack with _Back of the Room Hang_.
* `enc.sh` &ndash; encodes the video file for upload
