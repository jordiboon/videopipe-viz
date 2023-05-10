import pandas as pd
from moviepy.editor import *

from core_viz import *

# this can be empty if the video file and its videopipe output are at the same
# location as the code
path = ''
v_name = 'HIGH_LIGHTS_I_SNOWMAGAZINE_I_SANDER_26'
task = '_still_picker_output'
w, h = 1920, 1080

# Set output filename.
output_filename = 'thumbnail_output.gif'

# Set duration frame and text clips.
duration_f = 3
duration_t = 1

def read_still_picker(path, v_name):
    '''
    Read the JSON file with the still picker data.
    '''
    thumbnail = pd.read_json(path + v_name + '/' + v_name + task + '.json', lines = True)
    thumbnail_frames = [f for f in thumbnail.thumbnails_by_frameindex]
    return thumbnail_frames

def top_still_frames(thumbnail_frames, frame_amt=10):
    '''
    Return the id of top frames thumbnail frames based on the value in the JSON file.
    '''
    # Only get the value of each key
    frames = [{'rank': v['rank'], 'frame': v['frame']} for d in thumbnail_frames for k, v in d.items()]

    # Sort frames based on rank
    frames = sorted(frames, key = lambda i: i['rank'])
    frames = [frame_id['frame'] for frame_id in frames[:frame_amt][::-1]]
    return frames

clip = read_clip(v_name)
fps = clip.fps
frame_duration = 1/fps

# Set how many frames are included in the clip.
frame_amt = 10

# Read JSON and get top frames.
thumbnail_frames = read_still_picker(path, v_name)
top_frames = top_still_frames(thumbnail_frames, frame_amt)

# Create the txt and img clips.
thumbnail_clips = create_top_frame_clip(clip, top_frames, duration_f=duration_f, duration_t=duration_t)

# Create the final clip.
thumbnail_clip = concatenate_videoclips(thumbnail_clips)
thumbnail_clip.write_gif(output_filename, fps=1)
