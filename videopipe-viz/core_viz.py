from PIL import Image
from moviepy.editor import VideoFileClip
import subprocess
import os

def change_moviepy_ffmpeg():
    try:
        from moviepy.config import change_settings
        change_settings({"FFMPEG_BINARY":"ffmpeg"})
    except:
        pass

def get_frame(clip, frame_number, frame_duration):
    return Image.fromarray(clip.get_frame(frame_number * frame_duration))

def read_clip(v_name):
    clip = VideoFileClip(v_name + '.mp4')
    return clip

def write_audioclip(clip, v_name, logger=None):
    audio = clip.audio
    audio.write_audiofile(v_name + '_audio.mp3', logger=logger)

def write_clip(clip, name, postfix = '', audio=True, fps=25, logger=None):
    # Try hw acceleration, else use cpu.
    try:
        clip.write_videofile(name + '_' + postfix + '.mp4', codec='h264_nvenc', fps=fps, logger=logger, audio=audio, preset='3')
    except:
        try:
            clip.write_videofile(name + '_' + postfix + '.mp4', codec='libx264', fps=fps, logger=logger, audio=audio, preset='ultrafast')
        except:
            raise Exception('An error occured while writing the video file.')

def concatenate_videofiles(filename, output_name):
    subprocess.call("ffmpeg -f concat -safe 0 -i " + filename + " -c copy -y " + output_name, shell=True)

def add_audio_to_video(video_name, audio_name, output_name):
    subprocess.call("ffmpeg -i " + video_name + " -i " + audio_name + " -c:v copy -c:a aac -map 0:v:0 -map 1:a:0 -shortest -y " + output_name, shell=True)

def clean_up_files(v_name, rounds, txt_filename, output_filename='temp.mp4'):
    # Delete all the subclips.
    for i in range(rounds):
        os.remove(v_name + '_' + str(i) + '.mp4')

    # Delete the face_detection.txt file.
    os.remove(txt_filename)

    # Delete the audio file.
    if os.path.exists(v_name + '_audio.mp3'):
        os.remove(v_name + '_audio.mp3')

    if os.path.exists(output_filename):
        os.remove(output_filename)