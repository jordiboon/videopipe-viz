import pandas as pd
import numpy as np
import moviepy.editor as mp
from PIL import Image
from PIL import ImageDraw

from core_viz import *

def read_face_detection(path, v_name, task):
    '''
    Read the face detection JSON file.
    '''
    faces = pd.read_json(path + v_name + '/' + v_name + task + '.json', lines = True)
    faces_detected = [f for f in faces.data[0] if len(f['faces']) > 0]
    return faces_detected

def draw_bounding_boxes(clip, faces, img, color='red', bb_width=5):
    '''
    Draw all bounding boxes on the detected faces of the image.

    clip: movie clip
    faces: list of detected faces
    img: frame on which we draw the bounding boxes
    color: color of the bounding box
    bb_width: width of the bounding box

    '''
    for face in faces['faces']:
        scaled_bb = scale_bb_to_image(clip, *face['bb_faces'])
        draw = ImageDraw.Draw(img)
        draw.rectangle(scaled_bb, outline=color, width=bb_width)

    return img

def make_frame(clip, faces):
    """ Draw the faces on top of the frame in 'clip' and also return the corresponding frame timestamp. """
    face_frame_number = faces['dimension_idx']
    face_timestamp = face_frame_number / clip.fps
    frame = get_frame_by_number(clip, face_frame_number)
    bb_frame = draw_bounding_boxes(frame, faces['faces'])

    return face_timestamp, bb_frame

def get_face_clips(clip, faces_detected, face_frame_duration, timestamp_offset=0):
    """ Make a list of clips with all the face frames in 'faces_detected' inserted in 'clip'.
    face_frames are inserted with a duration of 'face_frame_duration'.
    'timestamp_offset' is used to determine the starting time of the first (faceless) subclip.
    """

    clips = []
    for faces in faces_detected:
        ts, bb_frame = make_frame(clip, faces)

        if (timestamp_offset != ts):
            clips.append(clip.subclip(timestamp_offset, ts))

        face_frame_clip = mp.ImageClip(np.asarray(bb_frame),
                                       duration=face_frame_duration)
        clips.append(face_frame_clip)
        timestamp_offset = ts + face_frame_duration

    return clips, timestamp_offset

if __name__ == '__main__':

    # Names of path, videofile and type of JSON.
    # Path can be empty if the video file and its videopipe output are at the same.

    #command-line call structure proposal:
    #face_detection.py video_path json_folder_path(optioneel)
    video_path = 'Videos/'
    v_name = 'D9003811_RUNNING_JEAN-PIERRE'
    task = '_face_detection_datamodel'
    RESIZE_DIM = 640
    w, h = 1920, 1080
    output_filename = 'output.mp4'
    duration_t = 1/25

    faces_detected = read_face_detection(video_path, v_name, task)
    v_name = video_path + v_name

    clip = read_clip(v_name)
    fps = clip.fps
    frame_duration = 1 / fps

    faces_per_round = 100
    face_frame_duration = frame_duration
    prev_ts = 0

    f = open('face_detection.txt', 'w')

    # Create video clips with 'faces_per_round' amount of detected faces inserted per clip.
    for round in range(len(faces_detected) // faces_per_round + 1):
        clips = []
        start_face_number = round * faces_per_round
        end_face_number = start_face_number + faces_per_round
        face_batch = faces_detected[start_face_number:end_face_number]
        clips, prev_ts = get_face_clips(clip, face_batch, face_frame_duration, prev_ts)

        # TODO: Add final subclip if there are no more faces to be added.
        write_clip(mp.concatenate_videoclips(clips))
        f.write('file face_detection_' + str(round) + '.mp4\n')
    f.close()

files_to_video(clip, v_name, 'face_detection.txt', output_filename)