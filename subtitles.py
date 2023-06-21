import pandas as pd
import srt
import numpy as np
from datetime import timedelta

def read_subs_json(path, v_name):
    '''
    Read the JSON files for language identification, speech gaps and speech recognition.
    Language identification is used to determine the original language of the video.
    Speech gaps are used to determine the parts of the video where there is no speech.
    Speech recognition is used to determine the speech, the language of the speech and the transcription confidence.
    '''
    language_id = pd.read_json(path + v_name + '/' + v_name + '_language_identification_datamodel.json', lines= True)
    speech_gaps = pd.read_json(path + v_name + '/' + v_name + '_speech_gaps_datamodel.json', lines= True)
    speech_recog = pd.read_json(path + v_name + '/' + v_name + '_whisper_subtitle_creation_datamodel.json', lines= True)
    return language_id, speech_gaps, speech_recog

def speech_single_sub(sub, idx=0, og_language='English'):
    '''
    Create a subtitle object for a single speech recognition object.
    '''
    start = timedelta(seconds = sub['start_time'])
    end = timedelta(seconds = sub['end_time'])
    if og_language != sub['language']:
        sub = srt.Subtitle(index = idx, start = start, end = end, content = '[' + sub['language'] + ' conf: ' + '{:.2f}'.format((np.exp(sub['translation_confidence']) * 100)) + '%]' \
                            + ' ' + sub['sentence'] + '\n' + '[' + og_language + '] ' + sub['original_sentence'] + '\n' + 'transcription conf: ' + '{:.2f}'.format((np.exp(sub['avg_logprob']) * 100)) + '%')
    else:
        sub = srt.Subtitle(index = idx, start = start, end = end, content = '[' + sub['language'] + '] ' + sub['sentence'] + '\n' + 'transcription conf: ' + '{:.2f}'.format((np.exp(sub['avg_logprob']) * 100)) + '%')
    return sub

def gaps_single_sub(sub, idx=0):
    '''
    Create a subtitle object for a single speech gap object.
    '''
    start = timedelta(seconds = sub['dimension_idx'] * frame_duration)
    end = timedelta(seconds = (sub['end']) * frame_duration)
    sub = srt.Subtitle(index = idx, start = start, end = end, content = '[...]')
    return sub

def gaps_single_sub_no_overlap(sub, speech, last_speech, idx=0):
    '''
    Create a subtitle object for a single speech gap object. This function
    ensures that the speech gap does not overlap with the speech by comparing
    start and end times of the speech gap and the previous and next speech.
    '''
    start = timedelta(seconds = sub['dimension_idx'] * frame_duration)
    end = timedelta(seconds = (sub['end']) * frame_duration)

    if speech:
        start_speech = timedelta(seconds = speech['start_time'])
        if start_speech < end:
            end = start_speech

    end_last_speech = timedelta(seconds = last_speech['end_time'])

    if end_last_speech > start:
        start = end_last_speech

    sub = srt.Subtitle(index = idx, start = start, end = end, content = '[...]')
    return sub

def speech_subs(speech, og_language='English'):
    '''
    Create srt file with speech.
    '''
    subs = []
    ind = 0
    for i in speech:
        sub = speech_single_sub(i, ind, og_language)
        subs.append(sub)
        ind += 1

    subs = srt.compose(subs)
    with open('subs.srt', 'w') as f:
        f.write(subs)

def gaps_subs(gaps):
    '''
    Create srt file with speech gaps.
    '''
    subs = []
    ind = 0
    for i in gaps:
        sub = gaps_single_sub(i, ind)
        subs.append(sub)
        ind += 1

    subs = srt.compose(subs)
    with open('gaps.srt', 'w') as f:
        f.write(subs)

def combine_subs(speech, gaps, og_language='English', allow_overlap=False):
    '''
    Create srt file with both speech and speech gaps. If allow_overlap is set to True,
    the speech gaps will overlap with the speech. If allow_overlap is set to False,
    the speech gaps will be trimmed to not overlap with the speech.
    '''
    subs = []
    ind = 0
    last_speech = None
    while True:
        try:
            start = timedelta(seconds = speech[0]['start_time'])
            start_gap = timedelta(seconds = gaps[0]['dimension_idx'] * frame_duration)
        except:
            print('No detected speech or gaps. Unable to combine subtitles.')
            exit()

        # Add either speech or gap depending on which starts first.
        if start < start_gap:
            sub = speech_single_sub(speech[0], ind, og_language)
            last_speech = speech[0]
            speech.pop(0)
        else:
            if allow_overlap:
                sub = gaps_single_sub(gaps[0], ind)
            else:
                sub = gaps_single_sub_no_overlap(gaps[0], speech[0], last_speech, ind)
            gaps.pop(0)

        subs.append(sub)
        ind += 1

        # If there are no more speech or gaps, add the remaining speech or gaps.
        if len(gaps) == 0:
            # Add remaining speech
            for i in speech:
                sub = speech_single_sub(i, ind, og_language)
                subs.append(sub)
                ind += 1
            break
        elif len(speech) == 0:
            # Add remaining gaps
            for i in gaps:
                if allow_overlap:
                    sub = gaps_single_sub(i, ind)
                else:
                    sub = gaps_single_sub_no_overlap(i, None, last_speech, ind)
                subs.append(sub)
                ind += 1
            break

    subs = srt.compose(subs)
    with open('combined_subs.srt', 'w') as f:
        f.write(subs)

if __name__ == '__main__':
    import argparse

    def_path = 'Videos/'
    def_v_name = 'HIGH_LIGHTS_I_SNOWMAGAZINE_I_SANDER_26'
    def_allow_overlap = False

    parser = argparse.ArgumentParser()
    parser.add_argument('video_path', default=def_path, nargs='?')
    parser.add_argument('v_name', default=def_v_name, nargs='?')
    parser.add_argument('allow_overlap', default=False, type=lambda x: (str(x).lower() in ['true','1', 'yes', 'y']), nargs='?')

    args = parser.parse_args()
    path = args.video_path
    v_name = args.v_name
    allow_overlap = args.allow_overlap

    frame_duration = 1/25

    language_id, speech_gaps, speech_recog = read_subs_json(path, v_name)
    og_language = language_id['data'][0][0]['language']
    speech = [f for f in speech_recog.data[0]]
    gaps = [f for f in speech_gaps.data[0]]
    speech_subs(speech, og_language)
    gaps_subs(gaps)
    combine_subs(speech, gaps, og_language, allow_overlap)
