import pandas as pd
from moviepy.editor import *

from core_viz import *

# this can be empty if the video file and its videopipe output are at the same
# location as the code.
path = ''
v_name = 'HIGH_LIGHTS_I_SNOWMAGAZINE_I_SANDER_26'
task = '_shot_boundaries_datamodel'
w, h = 1920, 1080
RESIZE_DIM = 640

# Set output filename.
output_filename = 'output.mp4'

# Set length of each shot boundary image.
duration_t = 1

def read_shot_detection(path, v_name):
    '''
    Read the JSON file with the shot detection data.
    '''
    shots = pd.read_json(path + v_name + '/' + v_name + task + '.json', lines = True)
    shots_detected = [f for f in shots.data[0]]
    return shots_detected

def create_shot_clip(txt, txtclip_dur=1/25, color='white', font="Century-Schoolbook-Roman", fontsize=70, kerning=-2, interline=-1, bg_color='black', size = (w, h)):
    '''
    Create frame of length txtclip_dur with txt in the center.
    '''
    txtclip = (TextClip(txt, color=color,
            font=font, fontsize=fontsize, kerning=kerning,
            interline=interline, bg_color=bg_color, size = (w, h))
            .set_duration(txtclip_dur)
            .set_position(('center')))
    return txtclip


def get_shot_clips(clip, shots_detected, shots_limit=25, timestamp=0.0, frame_duration=1/25, duration_t=1):
    '''
    Returns a list of clips with the shot boundaries and the shots themselves. shots_limit determines
    how many shot boundaries are included.
    '''
    clips = []
    shot_count = 0
    for shot in shots_detected:
        if shot_count == shots_limit:
            break

        txtclip = create_shot_clip('Shot ' + str(shot_count + 1), duration_t)
        timestamp = shot['dimension_idx'] * frame_duration

        subclip = clip.subclip(timestamp, timestamp + shot['duration'] * frame_duration + frame_duration)

        clips.append(txtclip)
        clips.append(subclip)
        shot_count += 1

        if shot == shots_detected[-1]:
            clips.append(clip.subclip(timestamp, clip.duration))
            timestamp = clip.duration

    return clips, timestamp

# This determines how much of the JSON is read before writing the video.
# Increasing this value will increase memory usage.
shots_limit = 20

clip = read_clip(v_name)
fps = clip.fps
frame_duration = 1/fps

shots_detected = read_shot_detection(path, v_name)

prev_t = 0

txt_filename = 'shot_boundaries.txt'

f = open(txt_filename, 'w')

rounds = len(shots_detected) // shots_limit + 1

# Get shot clips and write them to file. Then concatenate the files.
for i in range(rounds):
    clips = []
    clips, prev_t = get_shot_clips(clip, shots_detected[i * shots_limit:], shots_limit, prev_t, frame_duration, duration_t)
    clips = concatenate_videoclips(clips)
    write_clip(clips, v_name, str(i), fps=fps)
    f.write('file ' + v_name + '_' + str(i) + '.mp4\n')
f.close()

concatenate_videofiles(txt_filename, output_filename)
clean_up_files(v_name, rounds, txt_filename)