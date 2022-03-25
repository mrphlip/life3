#!/bin/bash
mencoder mf://*.png -mf fps=30 -audiofile out.wav -o out.avi -ovc lavc -oac mp3lame
