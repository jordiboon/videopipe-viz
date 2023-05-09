import pandas as pd
from moviepy.editor import *
from PIL import ImageDraw
from numpy import asarray

from core_viz import *

# Change ffmpeg used by moviepy to the one installed if one is installed, otherwise use the one from moviepy.
# This is necessary for using HW acceleration.
change_moviepy_ffmpeg()

# this can be empty if the video file and its videopipe output are at the same
# location as the code
path = ''
v_name = 'HIGH_LIGHTS_I_SNOWMAGAZINE_I_SANDER_26'
task = '_frame_face_detection_datamodel'
w, h = 1920, 1080
RESIZE_DIM = 640
output_filename = 'output.mp4'
duration_t = 1/25

def read_face_detection(path, v_name, task):
    faces = pd.read_json(path + v_name + '/' + v_name + task + '.json', lines = True)
    faces_detected = [f for f in faces.data[0] if len(f['faces']) > 0]
    return faces_detected

def draw_bounding_boxes(face, img, width_ratio, height_ratio, color = 'red', width = 5):
    for i in range(len(face['faces'])):
        y0, x1, y1, x0 = face['faces'][i]['bb_faces']
        y0 = int(y0 * height_ratio)
        y1 = int(y1 * height_ratio)
        x0 = int(x0 * width_ratio)
        x1 = int(x1 * width_ratio)

        draw = ImageDraw.Draw(img)
        draw.rectangle([x0, y0, x1, y1], outline=color, width=width)
    return img

def get_face_clips(faces_detected, faces_limit=100, timestamp=0, frame_duration=1/25, duration_t=1/25):
    clips = []
    face_count = 0
    for face in faces_detected:
        if face_count == faces_limit:
            break

        img = get_frame(clip, face['dimension_idx'], frame_duration)
        t = face['dimension_idx'] * frame_duration

        w, h = img.size
        width_ratio = w / RESIZE_DIM
        height_ratio = h / RESIZE_DIM

        draw_bounding_boxes(face, img, width_ratio, height_ratio)

        if (timestamp != t):
            clips.append(clip.subclip(timestamp, t))
        clips.append(ImageClip(asarray(img), duration=duration_t))
        img.close()
        timestamp = t + frame_duration
        face_count += 1

        # Add final clip if it is the last face.
        if face == faces_detected[-1]:
            clips.append(clip.subclip(timestamp, clip.duration))
            timestamp = clip.duration

    return clips, timestamp

# This determines how much of the JSON is read before writing the video.
# Increasing this value will increase memory usage.
faces_limit = 100

# Read the video file and its videopipe output.
clip = read_clip(v_name)
fps = clip.fps

frame_duration = 1 / fps

if duration_t == frame_duration:
    retain_audio = False
    write_audioclip(clip, v_name)
else:
    retain_audio = True

faces_detected = read_face_detection(path, v_name, task)

txt_filename = 'face_detection.txt'
f = open(txt_filename, 'w')

rounds = len(faces_detected) // faces_limit + 1
prev_t = 0

# Create video clips with detected faces and concatenate them into one video.
for i in range(rounds):
    clips = []
    clips, prev_t = get_face_clips(faces_detected[i * faces_limit:], faces_limit, prev_t, frame_duration, duration_t)

    write_clip(concatenate_videoclips(clips), v_name, str(i), retain_audio, fps)
    f.write('file ' + v_name + '_' + str(i) + '.mp4\n')
f.close()

if retain_audio:
    concatenate_videofiles(txt_filename, output_filename)
else:
    concatenate_videofiles(txt_filename, 'temp.mp4')
    add_audio_to_video('temp.mp4', v_name + '_audio.mp3', output_filename)

clean_up_files(v_name, rounds, txt_filename, 'temp.mp4')