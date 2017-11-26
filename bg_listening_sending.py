import threading
import queue
import time
import speech_recognition as sr
import datetime
import sys
import os
sys.path.append('third_party/Identification')
from IdentifyFile import identify_file

dict_id2name= {"e640526c-fd2c-415e-92ae-920f23f6c959":"Jonas",
        "0ba77bb5-d1d8-4f5c-ac7c-c0563c25046c": "Jacek",
        "a1237727-360d-450f-b79f-5abef984dcee": "Eduardo"}

def get_text_from_speech(audio):
    BING_KEY = "34fa73133d304049a259f06ffe6ef213"  # Microsoft Bing Voice Recognition API keys 32-character lowercase hexadecimal strings
    try:
        return r.recognize_bing(audio, key=BING_KEY)
    except sr.UnknownValueError:
        return "Audio not understood"
    except sr.RequestError as e:
        return "Could not request results from Microsoft Bing Voice Recognition service; {0}".format(e)

def get_speaker_from_wav(wav_fname, profile_ids):
    BING_KEY = "dfe8481d30814fa296829b9e6b3d6842"  # Microsoft Bing Voice Recognition API keys 32-character lowercase hexadecimal strings
    speaker_result = identify_file(BING_KEY, wav_fname, "true", profile_ids[:])
    speaker_name = ""
    if speaker_result['Identified Speaker'] == "00000000-0000-0000-0000-000000000000":
        speaker_name = "Undetermined"
    else:
        speaker_name = dict_id2name[speaker_result['Identified Speaker']]
    os.remove(wav_fname)
    return speaker_name
    
text_q = queue.Queue()
speaker_q= queue.Queue()
text_results, speaker_results= [], []

def process_text_queue():
    while True:
        audio = text_q.get()
        text = get_text_from_speech(audio)
        text_results.append(text)
        text_q.task_done()

def process_speaker_queue():
    while True:
        wav_fname = speaker_q.get()
        prof_ids = ["e640526c-fd2c-415e-92ae-920f23f6c959", "0ba77bb5-d1d8-4f5c-ac7c-c0563c25046c", "a1237727-360d-450f-b79f-5abef984dcee"]
        speaker = get_speaker_from_wav(wav_fname, prof_ids)
        speaker_results.append(speaker)
        speaker_q.task_done()

num_worker_threads=3
for i in range(num_worker_threads):
    t = threading.Thread(target=process_text_queue)
    t.daemon = True
    t.start()

for i in range(num_worker_threads):
    t = threading.Thread(target=process_speaker_queue)
    t.daemon = True
    t.start()

r = sr.Recognizer()
m = sr.Microphone(sample_rate = 16000)
with m as source:
    r.adjust_for_ambient_noise(source)  # we only need to calibrate once, before we start listening
print("Background adjusting done")

while True:
    with m as source:
        audio = r.listen(m, phrase_time_limit = 4)
        text_q.put(audio)
        timestamp = datetime.datetime.now().time()
        fname = "recording_{0}_{1}_{2}_{3}.wav".format(timestamp.hour, timestamp.minute, timestamp.second, timestamp.microsecond)
        with open(fname, "wb") as f:
            f.write(audio.get_wav_data())
            speaker_q.put(fname)
        print("speakers: ", speaker_results)
        print("text: ", text_results)
