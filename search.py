#!/usr/bin/python

import os
import sys
import json

from itertools import islice
from youtube_comment_downloader import *

url = sys.argv[1]
lim = int(sys.argv[2])

downloader = YoutubeCommentDownloader()
comments = downloader.get_comments_from_url(url, sort_by=SORT_BY_POPULAR)

for idx, comment in enumerate(islice(comments, lim)):
    print("")
    print(comment['text'])
    print("")
    print(f"Select comment as new chapters.txt? [(y)es / (e)dit / (n)o] ({idx+1}/{lim})")
    key = input()
    if(key == "y" or key == "e"):
        with open ("chapters.txt", "w") as f:
            f.write(comment['text'])
        if(key == "e"):
            os.system(f"{os.environ['EDITOR']} chapters.txt")
        break
