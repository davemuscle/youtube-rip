#!/usr/bin/python

# edited from: https://ikyle.me/blog/2020/add-mp4-chapters-ffmpeg

import re

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

with open('chapters.txt', 'r') as f:
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

for i in range(len(chapters)-1):
    chap = chapters[i]
    title = chap['title']
    start = chap['startTime']
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
