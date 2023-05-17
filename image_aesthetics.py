import pandas as pd
from moviepy.editor import *

from core_viz import *

# this can be empty if the video file and its videopipe output are at the same
# location as the code
path = ''
v_name = 'HIGH_LIGHTS_I_SNOWMAGAZINE_I_SANDER_26'
task = '_image_aesthetics_datamodel'
w, h = 1920, 1080

# Set output filename.
aesthetics_output_filename = 'aesthetics_output.gif'
technical_output_filename = 'technical_output.gif'
both_output_filename = 'both_output.gif'

# Set duration frame and text clips.
still_duration = 3
text_frame_duration = 1

def read_image_aesthetics(path, v_name):
    '''
    Read the JSON file with the image aesthetics data.
    '''
    aesthetics = pd.read_json(path + v_name + '/' + v_name + task + '.json', lines = True)
    aesthetics_detected = [f for f in aesthetics.data[0]]
    return aesthetics_detected

def top_aesthetic_frames(aesthetics_detected, frame_amt=10):
    '''
    Return the id of the top frames based on aesthetics, technical, and both in reverse order.
    '''
    highest_aesthetics = sorted(aesthetics_detected, key = lambda x: x['aesthetics_score'], reverse = True)
    highest_technical = sorted(aesthetics_detected, key = lambda x: x['technical_score'], reverse = True)

    # Get highest of both.
    highest = sorted(aesthetics_detected, key = lambda x: x['aesthetics_score'] + x['technical_score'], reverse = True)

    # Top frames from lowest to highest
    top_aesthetics = [f['dimension_idx'] for f in reversed(highest_aesthetics[:frame_amt])]
    top_technical = [f['dimension_idx'] for f in reversed(highest_technical[:frame_amt])]
    top_both = [f['dimension_idx'] for f in reversed(highest[:frame_amt])]

    return top_aesthetics, top_technical, top_both

clip = read_clip(v_name)
fps = clip.fps
frame_duration = 1/fps

# Set how many frames are included in the clip.
frame_amt = 10

# Read JSON and get top frames.
aesthetics_detected = read_image_aesthetics(path, v_name)
top_aesthetics, top_technical, top_both = top_aesthetic_frames(aesthetics_detected, frame_amt)

# Create the txt and img clips.
aesthetics_clips = create_top_frame_clip(clip, top_aesthetics, still_duration=still_duration, text_frame_duration=text_frame_duration)
technical_clips = create_top_frame_clip(clip, top_technical, still_duration=still_duration, text_frame_duration=text_frame_duration)
both_clips = create_top_frame_clip(clip, top_both, still_duration=still_duration, text_frame_duration=text_frame_duration)

aesthetics_clips = concatenate_videoclips(aesthetics_clips)
technical_clips = concatenate_videoclips(technical_clips)
both_clips = concatenate_videoclips(both_clips)

# Write the final gifs.
aesthetics_clips.write_gif(aesthetics_output_filename, fps = 1)
technical_clips.write_gif(technical_output_filename, fps = 1)
both_clips.write_gif(both_output_filename, fps = 1)


