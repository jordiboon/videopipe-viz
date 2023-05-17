# pip install moviepy

from moviepy.editor import VideoFileClip
import pygame as pg  # only for visualizing in bare python
from PIL import Image
import numpy as np
# from PIL import ImageDraw
import pandas as pd

# this can be empty if the video file and its videopipe output are at the same
# location as the code
path = ''
v_name = 'HIGH_LIGHTS_I_SNOWMAGAZINE_I_SANDER_26'
task = '_face_detection_datamodel'
RESIZE_DIM = 640

# read face detection json
faces = pd.read_json(f"{path + v_name}/{v_name + task}.json", lines=True)
faces_detected = [f for f in faces.data[0] if len(f['faces']) > 0]

# read video file with moviepy

clip = VideoFileClip(v_name + '.mp4')

fps = clip.fps
frame_duration = 1 / fps

# play a subclip

# in bare python
clip.subclip(t_start=0*frame_duration, t_end=86*frame_duration).preview()
pg.quit()

clip.subclip(t_start=0*frame_duration, t_end=86*frame_duration).preview()

# in a notebook environment
clip.subclip(t_start=0*frame_duration,
             t_end=5*frame_duration).ipython_display()

# draw a bounding box on a single frame for the first detected face

frames = clip.iter_frames()

face_to_draw = faces_detected[0]

# this is slow
for i, f in enumerate(frames):
    if i == face_to_draw['dimension_idx']:
        IMG = Image.fromarray(f)

img = IMG

img.show()

w, h = img.size
width_ratio = w / RESIZE_DIM
height_ratio = h / RESIZE_DIM

y0, x1, y1, x0 = face_to_draw['faces'][0]['bb_faces']

img_array = np.array(img)

cropped_img_array = img_array[int(y0 * height_ratio): int(y1 * height_ratio),
                              int(x0 * width_ratio):  int(x1 * width_ratio)]
cropped_img = Image.fromarray(cropped_img_array)
cropped_img.show()

# TODO: figure out how PIL Image reads coordinates.
# Apparently not like our model out of the box.

# draw = ImageDraw.Draw(img)
# draw.rectangle(face_to_draw['faces'][0]['bb_faces'], None, 'red')
