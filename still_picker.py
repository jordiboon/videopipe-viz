import pandas as pd
from moviepy.editor import *
from PIL import Image
import numpy as np


def get_frame_by_number(clip, frame_number):
    """ Returns the frame from the clip by their frame_number. """

    frame_duration = 1 / clip.fps
    frame = clip.get_frame(frame_number * frame_duration)
    return Image.fromarray(frame)


def get_thumbnail_clips(clip, thumbnails, countdown=True, still_duration=3, text_frame_duration=1):
    """ Make a list of clips for all the (ascendingly sorted on rank) thumbnails in 'thumbnails',
    alternating with text clips indicating the rank. """

    if countdown:
        thumbnails = thumbnails[::-1]

    still_duration = 3
    text_frame_duration = 1

    start_frame = TextClip(f"Top {len(thumbnails)} thumbnails \n\n from \n\n {v_name}.mp4", fontsize = 50, color = 'white',
                            size=(w, h)).set_duration(still_duration)

    clips = [start_frame]

    for rank, thumbnail_frame_nr in thumbnails:
        txtclip = TextClip(f"{rank}.",
                        fontsize = 100,
                        color = 'white',
                        size=(w, h)
                        ).set_duration(text_frame_duration)
        frame = get_frame_by_number(clip, thumbnail_frame_nr)
        imgclip = ImageClip(np.array(frame)).set_duration(still_duration)
        clips.append(txtclip)
        clips.append(imgclip)

if __name__ == '__main__':

    # this can be empty if the video file and its videopipe output are at the same
    # location as the code
    path = ''
    v_name = 'HIGH_LIGHTS_I_SNOWMAGAZINE_I_SANDER_26'
    task = '_still_picker_output'
    w, h = 1920, 1080

    ## read thumbnail json

    thumbnail = pd.read_json(path + v_name + '/' + v_name + task + '.json', lines = True)
    thumbnail_frames = [f for f in thumbnail.thumbnails_by_frameindex]

    # Make a list of (rank, frame) for all thumbnails in the json, sorted by rank ascending.
    thumbnails = [(f['rank'], f['frame']) for _, f in thumbnail.thumbnails_by_frameindex[0].items()].sort()

    ## Read video file with moviepy

    clip = VideoFileClip(v_name + '.mp4')

    top_5_thumbnails = thumbnails[:5]
    clips = get_thumbnail_clips(clip, top_5_thumbnails)

    final_clip = concatenate_videoclips(clips)
    final_clip.write_gif(f"{v_name}_top_5_stills.gif", fps=1)