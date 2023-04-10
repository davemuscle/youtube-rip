#!/usr/bin/python

import json
import sys
import subprocess
import re
import os

file_rip = sys.argv[1]
file_json = json.loads(subprocess.check_output(
        f"ffprobe -i \'{file_rip}\' -v quiet -show_chapters -print_format json",
        shell = True
        ))

if(file_json['chapters'] == []):
    print("No chapters in ripped video, exiting splitter")
    sys.exit(1)

for chapter in file_json['chapters']:
    chapter['tags']['title'] = re.sub('^\s*[0-9]+\.\s*', '', chapter['tags']['title'])
    print(f"Splitting chapter: {chapter}")
    name = chapter['tags']['title'] + ".mp4"
    os.system(f"ffmpeg -i \"{file_rip}\" -v quiet -vcodec copy -acodec copy -ss {chapter['start_time']} -to {chapter['end_time']} \'{name}\'")
