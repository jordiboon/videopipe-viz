import pandas as pd
import srt
import numpy as np
from datetime import timedelta

path = 'Videos/'
v_name = 'HIGH_LIGHTS_I_SNOWMAGAZINE_I_SANDER_26'
frame_duration = 0.04
allow_overlap = False

def read_subs_json(path, v_name):
    language_id = pd.read_json(path + v_name + '/' + v_name + '_language_identification_datamodel.json', lines= True)
    speech_gaps = pd.read_json(path + v_name + '/' + v_name + '_speech_gaps_datamodel.json', lines= True)
    speech_recog = pd.read_json(path + v_name + '/' + v_name + '_whisper_subtitle_creation_datamodel.json', lines= True)
    return language_id, speech_gaps, speech_recog

def speech_single_sub(sub, idx=0, og_language='English'):
    start = timedelta(seconds = sub['start_time'])
    end = timedelta(seconds = sub['end_time'])
    if og_language != sub['language']:
        sub = srt.Subtitle(index = idx, start = start, end = end, content = '[' + sub['language'] + ' conf: ' + '{:.2f}'.format((np.exp(sub['translation_confidence']) * 100)) + '%]' \
                            + ' ' + sub['sentence'] + '\n' + '[' + og_language + '] ' + sub['original_sentence'] + '\n' + 'transcription conf: ' + '{:.2f}'.format((np.exp(sub['avg_logprob']) * 100)) + '%')
    else:
        sub = srt.Subtitle(index = idx, start = start, end = end, content = '[' + sub['language'] + '] ' + sub['sentence'] + '\n' + 'transcription conf: ' + '{:.2f}'.format((np.exp(sub['avg_logprob']) * 100)) + '%')
    return sub

def gaps_single_sub(sub, idx=0):
    start = timedelta(seconds = sub['dimension_idx'] * frame_duration)
    end = timedelta(seconds = (sub['end']) * frame_duration)
    sub = srt.Subtitle(index = idx, start = start, end = end, content = '[...]')
    return sub

def gaps_single_sub_no_overlap(sub, speech, last_speech, idx=0):
    start = timedelta(seconds = sub['dimension_idx'] * frame_duration)
    end = timedelta(seconds = (sub['end']) * frame_duration)
    start_speech = timedelta(seconds = speech['start_time'])
    end_last_speech = timedelta(seconds = last_speech['end_time'])
    if start_speech < end:
        end = start_speech
    if end_last_speech > start:
        start = end_last_speech
    sub = srt.Subtitle(index = idx, start = start, end = end, content = '[...]')
    return sub

def speech_subs(speech, og_language='English'):
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
    Create srt file with speech and gaps where the earliest start time is taken
    first.
    '''
    subs = []
    ind = 0
    last_speech = None
    while True:
        start = timedelta(seconds = speech[0]['start_time'])
        start_gap = timedelta(seconds = gaps[0]['dimension_idx'] * frame_duration)
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
                sub = gaps_single_sub(i, ind)
                subs.append(sub)
                ind += 1
            break

    subs = srt.compose(subs)
    with open('combined_subs.srt', 'w') as f:
        f.write(subs)

if __name__ == '__main__':
    language_id, speech_gaps, speech_recog = read_subs_json(path, v_name)
    og_language = language_id['data'][0][0]['language']
    speech = [f for f in speech_recog.data[0]]
    gaps = [f for f in speech_gaps.data[0]]
    speech_subs(speech, og_language)
    gaps_subs(gaps)
    combine_subs(speech, gaps, og_language, allow_overlap)
