import os
from moviepy.video.io.VideoFileClip import VideoFileClip

# Specify the path to the library directory
library_path = "/path/to/library/directory"

# Initialize variables
longest_time = 0
longest_file = ""

# Loop through each file in the library directory
for filename in os.listdir(library_path):
    # Check if the file is a video file
    if filename.endswith(".mp4") or filename.endswith(".avi") or filename.endswith(".mov"):
        # Get the full path to the file
        filepath = os.path.join(library_path, filename)
        
        # Read the video file and get its duration
        video = VideoFileClip(filepath)
        duration = video.duration
        
        # Check if the duration is longer than the current longest time
        if duration > longest_time:
            longest_time = duration
            longest_file = filename
            
# Check if the longest time is more than 58 minutes
if longest_time > 58*60:
    print("The longest video file is", longest_file, "with a length of", longest_time, "seconds.")
else:
    print("There are no video files longer than 58 minutes.")