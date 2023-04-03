# pip install moviepy

from moviepy.editor import *
import pygame as pg # only for visualizing in bare python
from PIL import Image
from PIL import ImageDraw
import pandas as pd

# this can be empty if the video file and its videopipe output are at the same
# location as the code
path = '' 
v_name = 'HIGH_LIGHTS_I_SNOWMAGAZINE_I_SANDER_26'
task = '_face_detection_datamodel'

## read face detection json

faces = pd.read_json(path + v_name + '/' + v_name + task + '.json', lines = True)


faces_detected = [f for f in faces.data[0] if len(f['faces']) > 0]

## read video file with moviepy

clip = VideoFileClip(v_name + '.mp4')

fps = clip.fps
frame_duration = 1 / fps

## play a subclip

# in bare python
clip.subclip(t_start=0*frame_duration, t_end=100*frame_duration).preview()
pg.quit()

# in a notebook environment
clip.subclip(t_start=0*frame_duration, t_end=5*frame_duration).ipython_display()



## draw a bounding box on a single frame for t he first detected face

frames = clip.iter_frames()

face_to_draw = faces_detected[0]

# this is slow
for i, f in enumerate(frames):
  if i == face_to_draw['dimension_idx']:
    img = Image.fromarray(f)

img.show()

draw = ImageDraw.Draw(img)
draw.rectangle(face_to_draw['faces'][0]['bb_faces'], None, 'red')
