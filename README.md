# YouTube_data
Extracting data from YouTube channels and videos

Google developer API key for YouTube data is required for this code 

This code extracts data from YouTube for any channel or video. List of datasets include
- Channel statistics
- List of all videos on channel
- statistics for any video using videoid from Youtube. Video id can be extracted using "video_list" method from yt_extract. Alternatively video URL can be used
- Comments for any video or list of videos using video ID
- Captions from any video using video id and channel id

yt_api.py is the main code consisting of class yt_extract. ALl methods defnied in the class can be used for above requirements

youtube_vs.ipynb contains a sample code demonstracting how to use yt_extract class and methods from yt_api.py

