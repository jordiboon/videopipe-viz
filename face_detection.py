import pandas as pd
import numpy as np
import moviepy.editor as mp
from PIL import Image
from PIL import ImageDraw
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


def draw_bounding_box(img, x0, y0, x1, y1):
    """ Draw a bounding box (consisting of the points x0, y0, x1, y1) on top of a frame. """
    copy = img.copy()
    draw = ImageDraw.Draw(copy)
    draw.rectangle([x0, y0, x1, y1], fill=None, outline='red', width=2)
    return copy


def draw_bounding_boxes(frame, faces):
    """ Draw all the bounding boxes in the list of faces on top of the frame. """
    frame_copy = frame.copy()
    for face in faces:
        scaled_bb = scale_bb_to_image(*face['bb_faces'])
        frame_copy = draw_bounding_box(frame_copy, *scaled_bb)

    return frame_copy


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

    path = ''
    video_path = 'Videos/'
    v_name = 'D9003811_RUNNING_JEAN-PIERRE'
    task = '_face_detection_datamodel'
    RESIZE_DIM = 640

    # Read face detection JSON
    faces = pd.read_json(f"{path + v_name}/{v_name + task}.json", lines=True)
    faces_detected = [f for f in faces.data[0] if len(f['faces']) > 0]
    v_name = video_path + v_name

    clip = mp.VideoFileClip(v_name + '.mp4')
    audio = clip.audio
    audio.write_audiofile(v_name + '_audio.mp3')

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

        mp.concatenate_videoclips(clips).write_videofile('face_detection_' + str(round) + '.mp4', codec='libx264', fps=fps, logger=None, audio=False)
        f.write('file face_detection_' + str(round) + '.mp4\n')
    f.close()

    # remove any existing output.mp4 file
    if os.path.exists('output.mp4'):
        os.remove('output.mp4')
    if os.path.exists(v_name + '_face_detection.mp4'):
        os.remove(v_name + '_face_detection.mp4')

    # Concatenate all the files in the face_detection.txt file into one final clip
    # and write to .mp4 file.
    subprocess.call("ffmpeg -f concat -safe 0 -i face_detection.txt -c copy output.mp4", shell=True)

    # Add audio to the final clip.
    subprocess.call("ffmpeg -i output.mp4 -i " + v_name + "_audio.mp3 -c:v copy -c:a aac -map 0:v:0 -map 1:a:0 -shortest " + v_name + "_face_detection.mp4", shell=True)

    # Delete all the subclips.
    for round in range(len(faces_detected) // faces_per_round + 1):
        os.remove('face_detection_' + str(round) + '.mp4')

    # Delete the face_detection.txt file.
    os.remove('face_detection.txt')

    # Delete the audio file.
    os.remove(v_name + '_audio.mp3')
