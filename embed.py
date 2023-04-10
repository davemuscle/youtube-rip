#!/usr/bin/python

# edited from: https://ikyle.me/blog/2020/add-mp4-chapters-ffmpeg

import re
import sys
import subprocess

mp4 = sys.argv[1]
txt = 'chapters.txt'

def filter (line):
    # 00:00:00 chapter
    x = re.match(r"(\d+):(\d+):(\d+)\s+(.*)", line)
    if(x):
        hrs = int(x.group(1))
        mins = int(x.group(2))
        secs = int(x.group(3))
        title = x.group(4)
        return (hrs, mins, secs, title)
    # 00:00 chapter
    x = re.match(r"(\d+):(\d+)\s+(.*)", line)
    if(x):
        hrs = 0
        mins = int(x.group(1))
        secs = int(x.group(2))
        title = x.group(3)
        return (hrs, mins, secs, title)
    # 1. chapter 00:00:00
    x = re.match(r"\d+\.\s+(.*)\s+(\d+):(\d+):(\d+)", line)
    if(x):
        title = x.group(1)
        hrs = int(x.group(2))
        mins = int(x.group(3))
        secs = int(x.group(4))
        return (hrs, mins, secs, title)
    # 1. chapter 00:00
    x = re.match(r"\d+\.\s+(.*)\s+(\d+):(\d+)", line)
    if(x):
        title = x.group(1)
        hrs = 0
        mins = int(x.group(2))
        secs = int(x.group(3))
        return (hrs, mins, secs, title)

chapters = list()

with open(txt, 'r') as f:
    for line in f:
        (hrs, mins, secs, title) = filter(line)
        minutes = (hrs * 60) + mins
        seconds = secs + (minutes * 60)
        timestamp = (seconds * 1000)
        chap = {
                "title": title,
                "startTime": timestamp
                }
        chapters.append(chap)

text = ""

duration = subprocess.check_output(f"ffprobe -i \'{mp4}\' -v quiet -show_entries format=duration | grep duration | sed 's/.*=//'", shell=True)
duration = int(1000*float(duration.decode('utf-8')))

for i in range(len(chapters)):
    chap = chapters[i]
    title = chap['title']
    start = chap['startTime']
    if(i == len(chapters)-1):
        end = duration
    else:
        end = chapters[i+1]['startTime']-1
    text += f"""
[CHAPTER]
TIMEBASE=1/1000
START={start}
END={end}
title={title}
"""

with open("FFMETADATAFILE", "a") as myfile:
    myfile.write(text)
