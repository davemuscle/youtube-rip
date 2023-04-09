#!/usr/bin/python

import json
import sys
import subprocess
import re

file_rip = sys.argv[1]
file_json = json.loads(subprocess.check_output(
        f"ffprobe -i \'{file_rip}\' -v quiet -show_chapters -print_format json",
        shell = True
        ))

for chapter in file_json['chapters']:
    chapter['tags']['title'] = re.sub('^\s*[0-9]+\.\s*', '', chapter['tags']['title'])
    print(chapter)


# ffmpeg -i Bethlehem\ -\ Dark\ Metal\ \(Full\ Album\)\ \[LWN7NZgsnIo\].mp4 -acodec copy -ss 0.0 -to 312.000 ch'0'.mp4
