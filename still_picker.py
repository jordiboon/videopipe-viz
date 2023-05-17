import pandas as pd
import moviepy.editor as mp

from core_viz import *

def read_still_picker(path, v_name):
    '''
    Read the JSON file with the still picker data.
    '''
    thumbnail = pd.read_json(path + v_name + '/' + v_name + task + '.json', lines = True)
    thumbnail_frames = [f for f in thumbnail.thumbnails_by_frameindex]
    return thumbnail_frames

def top_still_frames(thumbnail_frames, frame_amt=5):
    '''
    Returns a list of the top frame ids based on their rank in the JSON file
    in ascending order.
    '''
    # Only get the value of each key
    frames = [{'rank': v['rank'], 'frame': v['frame']} for d in thumbnail_frames for k, v in d.items()]

    # Sort frames based on rank
    frames = sorted(frames, key = lambda i: i['rank'])
    frames = [frame_id['frame'] for frame_id in frames[:frame_amt][::-1]]
    return frames

if __name__ == '__main__':

    # this can be empty if the video file and its videopipe output are at the same
    # location as the code
    path = ''
    v_name = 'HIGH_LIGHTS_I_SNOWMAGAZINE_I_SANDER_26'
    task = '_still_picker_output'
    w, h = 1920, 1080

    v_name = path + v_name

    # Set output filename.
    output_filename = 'thumbnail_output.gif'

    # Set duration frame and text clips.
    duration_f = 3
    duration_t = 1

    # Set amount of frames included in the gif.
    frame_amt = 5

    # Read video file.
    clip = read_clip(v_name)

    # Read JSON
    thumbnail_frames = read_still_picker(path, v_name)
    top_frames = top_still_frames(thumbnail_frames, frame_amt=frame_amt)

    # Create the txt and img clips.
    clips = create_top_frame_clip(clip, top_frames, duration_f=duration_f, duration_t=duration_t)

    # Create the final clips
    final_clip = mp.concatenate_videoclips(clips)
    final_clip.write_gif(f"{v_name}_top_" + str(frame_amt) + "_stills.gif", fps=1)