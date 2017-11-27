import speech_recognition as sr
from os import path
import os
import sys
sys.path.append('third_party/Identification')
from IdentifyFile import identify_file
from pydub import AudioSegment
from pydub.utils import make_chunks
import pickle
import wx
from wx.lib.pubsub import pub


dict_id2name= {"e640526c-fd2c-415e-92ae-920f23f6c959":"Jonas",
        "039594a5-0228-46af-bac8-e07f4b709cde": "Jacek",
        "a1237727-360d-450f-b79f-5abef984dcee": "Eduardo"}

class DemoPreprocessor:
    def __init__(self, read_orig_audio_file_path, chunk_size):
        self.orig_audio_file_path = read_orig_audio_file_path
        self.audio_file_paths= []
        audio_chunk_file_paths = self.chunk_original_wav(chunk_size)
        for fp in audio_chunk_file_paths:
            self.audio_file_paths.append(path.join(path.dirname(path.realpath(__file__)), fp))
        self.prof_ids = list(dict_id2name.values())
        self.data = []
        self.chunk_size = chunk_size

    def run(self):
        for c, sound_file in enumerate(self.audio_file_paths[:-1]):
            # use the audio file as the audio source
            r = sr.Recognizer()
            prev_timestamp = 0
            with sr.AudioFile(sound_file) as source:
                audio = r.record(source)  # read the entire audio file
                speaker_result = self.get_speaker_from_wav(sound_file)
                timestamp = prev_timestamp + self.chunk_size
                text_result = self.get_text_from_speech(audio)
                speaker_name = "" 
                if speaker_result['Identified Speaker'] == "00000000-0000-0000-0000-000000000000":
                    speaker_name = "Undetermined"
                else:
                    speaker_name = dict_id2name[speaker_result['Identified Speaker']]
                self.data.append({"user": speaker_name, "dt": timestamp/1000., "text": text_result})
                prev_timestamp = timestamp
                wx.CallAfter(pub.sendMessage, 'analyze.update', message=c/(len(self.audio_file_paths)-1)*100)

    def get_text_from_speech(self, audio):
        BING_KEY = "34fa73133d304049a259f06ffe6ef213"  # Microsoft Bing Voice Recognition API keys 32-character lowercase hexadecimal strings
        r = sr.Recognizer()
        try:
            return r.recognize_bing(audio, key=BING_KEY)
        except sr.UnknownValueError:
            return "Microsoft Bing Voice Recognition could not understand audio"
        except sr.RequestError as e:
            return "Could not request results from Microsoft Bing Voice Recognition service; {0}".format(e)
    
    def get_speaker_from_wav(self, wav_fname):
        BING_KEY = "dfe8481d30814fa296829b9e6b3d6842"  # Microsoft Bing Voice Recognition API keys 32-character lowercase hexadecimal strings
        speaker_res = identify_file(BING_KEY, wav_fname, "true", list(dict_id2name.keys()))
        return speaker_res
    
    def chunk_original_wav(self, chunk_length):
        myaudio = AudioSegment.from_file(self.orig_audio_file_path, "wav") 
        chunk_length_ms = chunk_length # pydub calculates in millisec
        chunks = make_chunks(myaudio, chunk_length_ms)
        chunk_names = []
        for i, chunk in enumerate(chunks):
            chunk_name = "chunk{0}.wav".format(i)
            chunk_names.append(chunk_name)
            print("exporting", chunk_name, chunk.export(chunk_name, format="wav"))
        return chunk_names

    def save(self, filepath):
        pickle.dump(self, open(filepath, "wb"))

    @staticmethod
    def read(filepath):
        return pickle.load(open(filepath, "rb"))

if __name__ == "__main__":
    demo_pp = demo_preprocessor("EmoFile.wav", 4000)
    demo_pp.run()
    print(demo_pp.data)
