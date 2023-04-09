#!/usr/bin/python

import sys
import json

from itertools import islice
from youtube_comment_downloader import *

url = sys.argv[1]
lim = int(sys.argv[2])

downloader = YoutubeCommentDownloader()
comments = downloader.get_comments_from_url(url, sort_by=SORT_BY_POPULAR)

for comment in islice(comments, lim):
    print("")
    print(comment['text'])
    print("")
    print("Select comment as chapters.txt? [y/N]")
    key = input()
    if(key == "y"):
        with open ("chapters.txt", "w") as f:
            f.write(comment['text'])
        break
