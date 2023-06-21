import pandas as pd
import moviepy.editor as mp

def read_still_picker(path, v_name):
    '''
    Read the JSON file with the still picker data.
    '''
    thumbnail = pd.read_json(path + v_name + '/' + v_name + task + '.json', lines=True)
    thumbnail_frames = [f for f in thumbnail.thumbnails_by_frameindex]
    return thumbnail_frames


def top_still_frames(thumbnail_frames, frame_amt=5):
    '''
    Returns a list of the top frame ids based on their rank in the JSON file
    in ascending order.
    '''
    # Only get the value of each key
    frames = [{'rank': v['rank'], 'frame': v['frame']}
              for d in thumbnail_frames for _, v in d.items()]

    # Sort frames based on rank
    frames = sorted(frames, key = lambda i: i['rank'])
    frames = [frame_id['frame'] for frame_id in frames[:frame_amt][::-1]]
    return frames


if __name__ == '__main__':
    from core_viz import *
    import argparse

    # Set default values if no arguments are given
    def_video_path = 'Videos/'
    def_v_name = 'HIGH_LIGHTS_I_SNOWMAGAZINE_I_SANDER_26'
    def_task = '_still_picker_output'
    def_output_filename = 'thumbnail_output'

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

    # Set duration frame and text clips.
    still_duration = 3
    text_frame_duration = 1

    # Set amount of frames included in the gif.
    frame_amt = 5

    # Read video file.
    clip = read_clip(video_path + input_filename)

    # Read JSON
    thumbnail_frames = read_still_picker(video_path, v_name)
    top_frames = top_still_frames(thumbnail_frames, frame_amt=frame_amt)

    # Create the txt and img clips.
    clips = create_top_frame_clip(clip, top_frames, still_duration=still_duration, text_frame_duration=text_frame_duration)

    # Create the final clips
    final_clip = mp.concatenate_videoclips(clips)
    final_clip.write_gif(f"{output_filename}.gif", fps=1)