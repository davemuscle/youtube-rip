#!/usr/bin/python

import sys
import json
import re
import os
import subprocess
from itertools import islice
from youtube_comment_downloader import *

OUTPUT_DIR = "/home/dave/Music"

class Ripper:

    # constants
    NUM_COMMENTS = 100
    CHAPTER_FILE = "chapters.txt"
    FFMETADATA = "metadata.txt"
    URL_FILE = "url.txt"
    THUMBNAIL = "thumbnail.png"

    # setup
    def __init__ (self,
        url = "",
        fmt = "",
        artist = "",
        album = "",
        year = "",
        keep = False
    ):
        self.url = url
        self.fmt = fmt
        self.artist = artist
        self.album = album
        self.year = year
        self.outputdir = ""
        self.keep = keep

    # return future filename based off youtube url and format
    def get_file (self, url, fmt):
        tmp = subprocess.check_output(
            f'yt-dlp {url} --print filename -f {fmt}',
            shell=True
        )
        return tmp.decode('utf-8').strip()

    # return the ID portion of the url
    def get_id (self, url):
        tmp = re.match(r".*watch\?v=(.*).*", url)
        return tmp.group(1)

    # return the filename but with the ID ripped off
    def get_shortfile (self, file, id):
        return file.replace(f" [{id}]","")

    # return 0 or 1 if the youtube video had chapters in the JSON
    def check_for_chapters (self, file):
        tmp = subprocess.check_output(
            f"ffprobe -v quiet -i \'{file}\' -show_chapters",
            shell=True
        )
        tmp = tmp.decode('utf-8').strip()
        if(tmp == ""):
            return 0
        else:
            return 1

    # download the comments from the video and parse through them
    # the user can choose to select a comment as-is, or select and
    # edit a comment in using the text editor stored in $EDITOR
    def search_for_chapters (self, url):
        downloader = YoutubeCommentDownloader()
        comments = downloader.get_comments_from_url(url, sort_by=SORT_BY_POPULAR)
        for idx, comment in enumerate(islice(comments, self.NUM_COMMENTS)):
            print("")
            print(comment['text'])
            print("")
            print((
                f"Select comment as new chapters.txt? "
                f"[(y)es / (e)dit / (n)o] ({idx+1}/{self.NUM_COMMENTS})"
            ))
            key = input()
            if(key == "y" or key == "e"):
                with open (self.CHAPTER_FILE, "w") as f:
                    f.write(comment['text'])
                if(key == "e"):
                    os.system(f"{os.environ['EDITOR']} {self.CHAPTER_FILE}")
                break

    # regex filtering for the selected youtube comment, detects between
    # multiple formats of listing out the timestamps of songs
    def filter_chapter_line (self, line):
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
        # chapter 00:00:00
        x = re.match(r"(.*)\s+(\d+):(\d+):(\d+)", line)
        if(x):
            title = x.group(1)
            hrs = int(x.group(2))
            mins = int(x.group(3))
            secs = int(x.group(4))
            return (hrs, mins, secs, title)
        # chapter 00:00
        x = re.match(r"(.*)\s+(\d+):(\d+)", line)
        if(x):
            title = x.group(1)
            hrs = 0
            mins = int(x.group(2))
            secs = int(x.group(3))
            return (hrs, mins, secs, title)

    # place the searched chapters into the metadata of the original source
    # edited from: https://ikyle.me/blog/2020/add-mp4-chapters-ffmpeg
    def embed_chapters (self, file):
        chapters = list()
        with open(self.CHAPTER_FILE, 'r') as f:
            for line in f:
                (hrs, mins, secs, title) = self.filter_chapter_line(line)
                minutes = (hrs * 60) + mins
                seconds = secs + (minutes * 60)
                timestamp = (seconds * 1000)
                chap = {
                        "title": title.title(),
                        "startTime": timestamp
                        }
                chapters.append(chap)

        cmd = (
            f"ffprobe -i \'{file}\' "
             "-v quiet "
             "-show_entries format=duration "
             "| grep duration | sed 's/.*=//'"
        )
        duration = subprocess.check_output(cmd, shell=True)
        duration = int(1000*float(duration.decode('utf-8')))

        text = ""
        for i, chap in enumerate(chapters):
            chap = chapters[i]
            title = chap['title']
            start = chap['startTime']
            if(i == len(chapters)-1):
                end = duration
            else:
                end = chapters[i+1]['startTime']-1
            text += (
                f"\n[CHAPTER]"
                f"\nTIMEBASE=1/1000"
                f"\nSTART={start}"
                f"\nEND={end}"
                f"\ntitle={title}\n"
            )

        os.system(f"rm -f {self.FFMETADATA}")
        os.system(f"ffmpeg -v quiet -i \'{file}\' -f ffmetadata {self.FFMETADATA}")
        with open(self.FFMETADATA, "a") as myfile:
            myfile.write(text)
        os.system(f"mv \'{file}\' .tmp.ffmpeg")
        os.system((
            f"ffmpeg -v quiet -i .tmp.ffmpeg -i {self.FFMETADATA} "
            f"-map_metadata 1 "
            f"-metadata author=\'{self.artist}\' "
            f"-metadata artist=\'{self.artist}\' "
            f"-metadata album_artist=\'{self.artist}\' "
            f"-metadata album=\'{self.album}\' "
            f"-metadata year=\'{self.year}\' "
            f"-metadata date=\'{self.year}\' "
            f"-codec copy \'{file}\'"
        ))
        os.system(f"rm -f .tmp.ffmpeg")

    # split the source into the corresponding chapters
    def split_chapters (self, file):
        file_json = json.loads(subprocess.check_output(
            f"ffprobe -i \'{file}\' -v quiet -show_chapters -print_format json",
            shell = True
        ))
        top = len(file_json['chapters'])
        for idx, chapter in enumerate(file_json['chapters']):
            title = chapter['tags']['title']
            # peel off the number from a title like: "1. xyz"
            tmp = re.match(r"^\s*\d+\.\s*(.*)", title)
            if(tmp):
                title = tmp.group(1)
            print(f"Creating chapter for: {title}")
            os.system((
                f"ffmpeg -i \'{file}\' -v quiet "
                f"-metadata author=\'{self.artist}\' "
                f"-metadata artist=\'{self.artist}\' "
                f"-metadata album_artist=\'{self.artist}\' "
                f"-metadata album=\'{self.album}\' "
                f"-metadata year=\'{self.year}\' "
                f"-metadata date=\'{self.year}\' "
                f"-metadata track=\"{idx+1}/{top}\" "
                f"-metadata title=\"{title}\" "
                f"-codec copy -ss {chapter['start_time']} -to {chapter['end_time']} "
                f"\'{title}.{self.fmt}\'"
            ))
            if(self.fmt == "m4a"):
                os.system(f"mp4art --add {self.THUMBNAIL} \'{title}.{self.fmt}\'")

    # top-level album ripper
    def rip(self):
        # Setup names
        self.file = self.get_file(self.url, self.fmt)
        self.id = self.get_id(self.url)
        self.shortfile = self.get_shortfile(self.file, self.id)
        
        # Download source
        os.system(f"yt-dlp {self.url} --add-metadata --embed-thumbnail -f {self.fmt}")

        # Write out the thumbnail
        os.system(f"ffmpeg -v quiet -i \'{self.file}\' -map 0:v -map -0:V -c copy {self.THUMBNAIL}")

        # Determine if there are chapters
        if(self.check_for_chapters(self.file) == 0):
            print((
                f"Source does not have chapters natively, run comment search? "
                "[(y)es / (n)o] "
            ))
            x = input()
            if(x != "n"):
                self.search_for_chapters(self.url)
            self.embed_chapters(self.file)

        # Split album into parts
        self.split_chapters(self.file)

        # Export url
        with open (self.URL_FILE, "w") as f:
            f.write(f"{self.url}\n")

        dir0 = self.outputdir + '/' + self.artist
        dir1 = dir0 + '/' + self.album

        # Remove source
        if(not self.keep):
            os.system(f"rm -f \'{self.file}\'")

        # Remove metadata and chapters, keep the url
        os.system(f"rm -f {self.CHAPTER_FILE}")
        os.system(f"rm -f {self.FFMETADATA}")

        # Export to directory
        os.system(f"mkdir -p \'{dir0}\'")
        os.system(f"mkdir -p \'{dir1}\'")
        os.system(f"mv * \'{dir1}\'/")

        print("Done ripping, optionally, run 'easytag' now for manual cleanup")
        print("Sent output to " + dir1)

# ../rip.py 'https://www.youtube.com/watch?v=GkUL_oOOhMk' mp4
if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("-u", "--url", action="store")
    parser.add_argument("-f", "--format", action="store")
    parser.add_argument("-a", "--artist", action="store")
    parser.add_argument("-b", "--album", action="store")
    parser.add_argument("-y", "--year", action="store")
    parser.add_argument("-k", "--keep", action="store_true")
    args = parser.parse_args()
    x = Ripper(
        url = args.url,
        fmt = args.format,
        artist = args.artist,
        album = args.album,
        year = args.year,
        keep = args.keep
    )
    x.outputdir = OUTPUT_DIR
    x.rip()
