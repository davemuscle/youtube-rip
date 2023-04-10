#!/usr/bin/sh

../clean.sh

URL=$1

FILE_ORIG=$(yt-dlp ${URL} --print filename -f mp4)

ID=$(echo ${URL} | sed 's/.*watch?v=//')
FILE=$(echo ${FILE_ORIG} | sed "s/ \[${ID}\]//")

yt-dlp ${URL} --add-metadata -f mp4
mv "${FILE_ORIG}" input.mp4
echo ${URL} > url.txt

chapters=$(ffprobe -v quiet -i input.mp4 -show_chapters)
if [ -z "${chapters}" ]
then
    read -p "Video does not have chapters, continue to perform a search" key
    echo "Performing search..."
    ../search.py ${URL} 100
    echo "Grabbing existing metadata for mp4"
    ffmpeg -v quiet -i input.mp4 -f ffmetadata FFMETADATAFILE
    echo "Embedding chapters.txt into metadata"
    ../embed.py input.mp4
    echo "Applying metadata back to mp4"
    ffmpeg -v quiet -i input.mp4 -i FFMETADATAFILE -map_metadata 1 -codec copy input_tmp.mp4
    mv input_tmp.mp4 input.mp4
    echo "Video now has chapters!"
else
    echo "Video has chapters!"
fi

../split.py input.mp4
