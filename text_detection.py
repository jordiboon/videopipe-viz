import pandas as pd
from moviepy.editor import *
from PIL import ImageDraw
from PIL import ImageFont
from numpy import asarray

from core_viz import *

# this can be empty if the video file and its videopipe output are at the same
# location as the code.
path = ''
v_name = 'HIGH_LIGHTS_I_SNOWMAGAZINE_I_SANDER_26'
task = '_frame_text_detection_datamodel'
w, h = 1920, 1080
RESIZE_DIM = 640

# Set output filename.
output_filename = 'output.mp4'

# Set duration of each text detected frame.
duration_t = 1/25

def read_text_detection(path, v_name):
    '''
    Read the text detection JSON file.
    '''
    text = pd.read_json(path + v_name + '/' + v_name + task + '.json', lines = True)
    texts_detected = [f for f in text.data[0] if len(f['text']) > 0]
    return texts_detected

def draw_text(texts, img, color='black', bb_color='red', font=ImageFont.truetype("Lato-Bold.ttf", 20), bb_width=3):
    '''
    Draw all detected texts on the image.
    '''
    for text in texts:
        left, top, width, height, conf, text = texts[text].values()
        draw = ImageDraw.Draw(img)
        draw.rectangle(((left, top), ((left + width), (top + height))), outline = bb_color, width = bb_width)
        text = text + " (conf: " + str(conf) + ")"
        draw.text((left, top), text, font=font, fill = color)
    return img

def get_text_clips(clip, texts_detected, texts_limit=100, timestamp=0, frame_duration=1/25, duration_t=1/25):
    '''
    Returns a list of clips with the text detected frames added. texts_limit
    determines how many text detected frames are added.
    '''
    clips = []
    text_count = 0
    for text in texts_detected:
        if text_count == texts_limit:
            break

        img = get_frame(clip, text['dimension_idx'], frame_duration)
        t = text['dimension_idx'] * frame_duration

        draw_text(text['text'], img)

        if (timestamp != t):
            clips.append(clip.subclip(timestamp, t))

        clips.append(ImageClip(asarray(img), duration=duration_t))
        img.close()
        timestamp = t + frame_duration
        text_count += 1

        if text == texts_detected[-1]:
            clips.append(clip.subclip(timestamp, clip.duration))
            timestamp = clip.duration

    return clips, timestamp

# This determines how much of the JSON is read before writing the video.
# Increasing this value will increase memory usage.
texts_limit = 100

# Requires font in /usr/share/fonts/truetype.
font = ImageFont.truetype("Lato-Bold.ttf", 20)

clip = read_clip(v_name)
fps = clip.fps
frame_duration = 1/fps

if duration_t == frame_duration:
    retain_audio = False
    write_audioclip(clip, v_name)
else:
    retain_audio = True

texts_detected = read_text_detection(path, v_name)

prev_t = 0

txt_filename = 'text_detection.txt'

f = open(txt_filename, 'w')

rounds = len(texts_detected) // texts_limit + 1

# Get text clips and write them to file. Then concatenate and add audio if
# necessary.
for i in range(rounds):
    clips = []
    clips, prev_t = get_text_clips(clip, texts_detected[i * texts_limit:], texts_limit, prev_t, frame_duration, duration_t)

    write_clip(concatenate_videoclips(clips), v_name, str(i), retain_audio, fps)
    f.write('file ' + v_name + '_' + str(i) + '.mp4\n')
f.close()

if retain_audio:
    concatenate_videofiles(txt_filename, output_filename)
else:
    concatenate_videofiles(txt_filename, 'temp.mp4')
    add_audio_to_video('temp.mp4', v_name + '_audio.mp3', output_filename)

clean_up_files(v_name, rounds, txt_filename, 'temp.mp4')