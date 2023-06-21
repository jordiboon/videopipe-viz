import pandas as pd
import numpy as np
from PIL import Image, ImageDraw, ImageFont


def get_frame_by_number(clip, frame_number):
    """ Returns the frame from the clip by their frame_number. """

    frame_duration = 1 / clip.fps
    frame = clip.get_frame(frame_number * frame_duration)
    return Image.fromarray(frame)


def make_frame_line(clip, midroll_marker):
    """ Make a row of frames indicating
    the frame-precise position of the midroll. """
    w, h = clip.size

    # If the midroll_marker in the JSON is an integer,
    # it indicates the frame after the midroll.
    # If the marker is a float e.g. '4.5' this indicates
    # that the midroll should be between frames 4 and 5.
    try:
        frame_after_midroll = int(midroll_marker)
        frame_before_midroll = frame_after_midroll - 1
    except ValueError:
        frame_before_midroll = int(float(midroll_marker))
        frame_after_midroll = int(np.ceil(float(midroll_marker)))

    frame_line = Image.new('RGB', (5 * w, h))

    frame_line.paste(get_frame_by_number(clip, frame_before_midroll - 1), (0, 0))
    frame_line.paste(get_frame_by_number(clip, frame_before_midroll), (w, 0))

    font = ImageFont.truetype("NotoSansMono-Bold.ttf", 50)
    draw = ImageDraw.Draw(frame_line)
    draw.text((2.2 * w, h/3), f"Midroll between frames {frame_before_midroll} and {frame_after_midroll}", font=font, fill='white')
    draw.text((2.2 * w, h/2), f"timestamps: {frame_before_midroll/clip.fps} and {frame_after_midroll/clip.fps}", font=font, fill='white')

    frame_line.paste(get_frame_by_number(clip, frame_after_midroll), (3 * w, 0))
    frame_line.paste(get_frame_by_number(clip, frame_after_midroll + 1), (4 * w, 0))

    return frame_line


if __name__ == '__main__':
    import core_viz as core
    import argparse

    # Set default values if no arguments are given
    def_video_path = 'Videos/'
    def_v_name = 'HIGH_LIGHTS_I_SNOWMAGAZINE_I_SANDER_26'
    def_task = '_midroll_marker_output'
    def_output_filename = 'midroll_output'

    parser = argparse.ArgumentParser()
    parser.add_argument('video_path', default=def_video_path, nargs='?')
    parser.add_argument('v_name', default=def_v_name, nargs='?')
    parser.add_argument('task', default=def_task, nargs='?')
    parser.add_argument('output_filename', default=def_output_filename, nargs='?')
    parser.add_argument('input_filename', default=def_v_name, nargs='?')

    args = parser.parse_args()
    video_path = args.video_path
    v_name = args.v_name
    task = args.task
    output_filename = args.output_filename
    input_filename = args.input_filename

    # read thumbnail json

    midroll = pd.read_json(f"{video_path + v_name}/{v_name + task}.json", lines=True)
    midroll_markers = midroll['midroll_markers'][0]

    # Read video file with moviepy

    clip = core.read_clip(video_path + input_filename)

    make_frame_line(clip, midroll_markers[0]).save(f"{output_filename}.jpg")