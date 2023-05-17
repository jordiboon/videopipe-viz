import pandas as pd
import moviepy.editor as mp

from core_viz import *

def read_shot_detection(path, v_name):
    '''
    Read the JSON file with the shot detection data.
    '''
    shots = pd.read_json(path + v_name + '/' + v_name + task + '.json', lines = True)
    shots_detected = [f for f in shots.data[0]]
    return shots_detected

def create_shot_clip(txt, txtclip_dur=1/25, color='white', font="Century-Schoolbook-Roman", fontsize=70, kerning=-2, interline=-1, bg_color='black'):
    '''
    Create frame of length txtclip_dur with txt in the center.
    '''
    txtclip = (mp.TextClip(txt, color=color,
            font=font, fontsize=fontsize, kerning=kerning,
            interline=interline, bg_color=bg_color, size = (w,h))
            .set_duration(txtclip_dur)
            .set_position(('center')))
    return txtclip

def get_shot_clips(clip, shots_detected, shot_frame_duration=1, shot_count=1):
    '''
    Returns a list of clips with the shot boundaries and the shots themselves. shots_limit determines
    how many shot boundaries are included.
    '''
    clips = []
    for shot in shots_detected:
        txtclip = create_shot_clip('Shot ' + str(shot_count), shot_frame_duration)
        timestamp = shot['dimension_idx'] * frame_duration

        subclip = clip.subclip(timestamp, timestamp + shot['duration'] * frame_duration + frame_duration)

        clips.append(txtclip)
        clips.append(subclip)
        shot_count += 1
    return clips, timestamp, shot_count

if __name__ == '__main__':
    # this can be empty if the video file and its videopipe output are at the same
    # location as the code.
    video_path = 'Videos/'
    v_name = 'HIGH_LIGHTS_I_SNOWMAGAZINE_I_SANDER_26'
    task = '_shot_boundaries_datamodel'
    RESIZE_DIM = 640
    output_filename = 'output.mp4'
    duration_t = 1

    shots_detected = read_shot_detection(video_path, v_name)

    v_name = video_path + v_name

    clip = read_clip(v_name)
    fps = clip.fps
    frame_duration = 1/fps
    w, h = clip.size

    shots_per_round = 20
    shot_frame_duration = 1
    prev_ts = 0
    shot_count = 1

    f = open('shot_detection.txt', 'w')

    # Get shot clips and write them to file. Then concatenate the files.
    for round in range(len(shots_detected) // shots_per_round + 1):
        clips = []
        start_shot_number = round * shots_per_round
        end_shot_number = start_shot_number + shots_per_round
        shot_batch = shots_detected[start_shot_number:end_shot_number]
        clips, prev_t, shot_count = get_shot_clips(clip, shot_batch, shot_frame_duration, shot_count)

        if (round == len(shots_detected) // shots_per_round):
            clips.append(clip.subclip(prev_t, clip.duration))

        write_clip(mp.concatenate_videoclips(clips), v_name, str(round), True)
        f.write('file ' + v_name + '_' + str(round) + '.mp4\n')
    f.close()

    files_to_video(clip, v_name, round, 'shot_detection.txt', output_filename, False)