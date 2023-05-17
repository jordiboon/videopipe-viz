from PIL import Image
from moviepy.editor import *
from numpy import asarray
import subprocess
import os

# Change the ffmpeg binary of moviepy to the local one to allow for hw acceleration.
try:
    from moviepy.config import change_settings
    change_settings({"FFMPEG_BINARY":"ffmpeg"})
except:
    pass

def get_frame(clip, frame_number, frame_duration=1/25):
    return Image.fromarray(clip.get_frame(frame_number * frame_duration))

def read_clip(v_name):
    clip = VideoFileClip(v_name + '.mp4')
    return clip

def create_text_clip(txt, txtclip_dur=1/25, color='white', font="Century-Schoolbook-Roman", fontsize=70, kerning=-2, interline=-1, bg_color='black', clipsize = (1920, 1080)):
    '''
    Create frame of length txtclip_dur with txt in the center.
    '''
    txtclip = (TextClip(txt, color=color,
            font=font, fontsize=fontsize, kerning=kerning,
            interline=interline, bg_color=bg_color, size = clipsize)
            .set_duration(txtclip_dur)
            .set_position(('center')))
    return txtclip

def create_top_frame_clip(clip, top_frames, duration_f=3, duration_t=1):
    '''
    Returns a clip of the top frames preceded by a clip showing the ranking of
    the clip.
    '''
    clips = []
    count = len(top_frames)
    for frame in top_frames:
        txtclip = create_text_clip('Frame ' + str(count), duration_t)
        f = get_frame(clip, frame)
        imgclip = ImageClip(asarray(f), duration=duration_f)
        clips.append(txtclip)
        clips.append(imgclip)
        count -= 1

    return clips

def write_audioclip(clip, v_name, logger=None):
    audio = clip.audio
    audio.write_audiofile(v_name + '_audio.mp3', logger=logger)

def write_clip(clip, name, postfix = '', audio=True, fps=25, logger=None):
    # Try hw acceleration, else use cpu.
    try:
        clip.write_videofile(name + '_' + postfix + '.mp4', codec='h264_nvenc', fps=fps, logger=logger, audio=audio, preset='fast')
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