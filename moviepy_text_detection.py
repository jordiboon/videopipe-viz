import pandas as pd
import numpy as np
from moviepy.editor import *
from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont
import os
import subprocess


def get_frame_by_number(clip, frame_number):
    """ Returns the frame from the clip by their frame_number. """

    frame_duration = 1 / clip.fps
    frame = clip.get_frame(frame_number * frame_duration)
    return Image.fromarray(frame)


def scale_bb_to_image(y0, x1, y1, x0):
    """ Scales a bounding box to the image using the global RESIZE_DIM variable. """

    w, h = clip.size
    width_ratio = w / RESIZE_DIM
    height_ratio = h / RESIZE_DIM

    y0 = int(y0 * height_ratio)
    y1 = int(y1 * height_ratio)
    x0 = int(x0 * width_ratio)
    x1 = int(x1 * width_ratio)

    return [x0, y0, x1, y1]


def draw_text_bb(frame, texts):
    """ Draw all the detected text in 'texts' on top of the frame. """
    copy = frame.copy()
    for text in texts:
        left, top, width, height, conf, detected_text = texts[text].values()
        right = left + width
        bottom = top + height
        draw = ImageDraw.Draw(copy)
        draw.rectangle([left, bottom, right, top], outline='blue', width=2)
        draw.text((left, bottom), detected_text, font=font, fill='blue')
    return copy


def make_frame(clip, txts):
    """ Get the frame in 'txts' and draw all the texts in 'txts' on top of the frame.
    Also return the timestamp in the clip of the detected frame.
    """
    txt_frame_number = txts['dimension_idx']
    txt_timestamp = txt_frame_number / clip.fps
    frame = get_frame_by_number(clip, txt_frame_number)
    bb_frame = draw_text_bb(frame, txts['text'])

    return txt_timestamp, bb_frame


def get_txt_clips(clip, texts_detected, txt_frame_duration, timestamp_offset=0):
    """ Make a list of clips with all the text frames in 'texts_detected' inserted in 'clip'.
    text frames are inserted with a duration of 'txt_frame_duration'.
    'timestamp_offset' is used to determine the starting time of the first (textless) subclip.
    """
    clips = []
    for txt in texts_detected:
        ts, bb_frame = make_frame(clip, txt)

        if (timestamp_offset != ts):
            clips.append(clip.subclip(timestamp_offset, ts))

        txt_frame_clip = ImageClip(np.asarray(bb_frame), duration=txt_frame_duration)
        clips.append(txt_frame_clip)
        timestamp_offset = ts + txt_frame_duration

    return clips, timestamp_offset


if __name__ == '__main__':
    path = ''
    video_path = 'Videos/'
    v_name = 'D9003811_RUNNING_JEAN-PIERRE'
    task = '_text_detection_datamodel'
    RESIZE_DIM = 640

    font = ImageFont.truetype("NotoSansMono-Bold.ttf", 20)

    texts_detected = pd.read_json(f"{path + v_name}/{v_name + task}.json", lines=True)
    txts_detected = [f for f in texts_detected.data[0] if len(f['text']) > 0]
    v_name = video_path + v_name

    clip = VideoFileClip(v_name + '.mp4')
    audio = clip.audio
    audio.write_audiofile(v_name + '_audio.mp3')

    fps = clip.fps
    frame_duration = 1 / fps

    txts_per_round = 100

    txt_frame_duration = frame_duration
    prev_ts = 0

    f = open('txt_detection.txt', 'w')

    # Create video clips with 'faces_per_round' amount of detected faces per clip.
    for round in range(len(txts_detected) // txts_per_round + 1):
        clips = []
        start_txt_number = round * txts_per_round
        end_txt_number = start_txt_number + txts_per_round
        txt_batch = txts_detected[start_txt_number:end_txt_number]
        clips, prev_ts = get_txt_clips(clip, txt_batch, txt_frame_duration, prev_ts)

        concatenate_videoclips(clips).write_videofile('txt_detection_' + str(round) + '.mp4', codec='libx264', fps=fps, logger=None, audio=False)
        f.write('file txt_detection_' + str(round) + '.mp4\n')
    f.close()

    # remove any existing output.mp4 file
    if os.path.exists('output.mp4'):
        os.remove('output.mp4')
    if os.path.exists(v_name + '_txt_detection.mp4'):
        os.remove(v_name + '_txt_detection.mp4')

    # Concatenate all the files in the txt_detection.txt file into one final clip
    # and write to .mp4 file.
    subprocess.call("ffmpeg -f concat -safe 0 -i txt_detection.txt -c copy output.mp4", shell=True)

    # Add audio to the final clip.
    subprocess.call("ffmpeg -i output.mp4 -i " + v_name + "_audio.mp3 -c:v copy -c:a aac -map 0:v:0 -map 1:a:0 -shortest " + v_name + "_txt_detection.mp4", shell=True)

    # Delete all the subclips.
    for round in range(len(txts_detected) // txts_per_round + 1):
        os.remove('txt_detection_' + str(round) + '.mp4')

    # Delete the txt_detection.txt file.
    os.remove('txt_detection.txt')

    # Delete the audio file.
    os.remove(v_name + '_audio.mp3')