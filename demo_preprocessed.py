import speech_recognition as sr
from os import path
import os
import sys
sys.path.append('third_party/Identification')
from IdentifyFile import identify_file
from pydub import AudioSegment
from pydub.utils import make_chunks
import pickle

class demo_preprocessor:
    def __init__(self, read_orig_audio_file_path, prof_ids, chunk_size):
        self.orig_audio_file_path = read_orig_audio_file_path
        self.audio_file_paths= []
        audio_chunk_file_paths = self.chunk_original_wav(chunk_size)
        for fp in audio_chunk_file_paths:
            self.audio_file_paths.append(path.join(path.dirname(path.realpath(__file__)), fp))
        self.prof_ids = prof_ids
        self.text_results = []
        self.speaker_results = []
        self.timestamps = [0]
        self.chunk_size = chunk_size

    def run(self):
        for sound_file in self.audio_file_paths[:-1]:
            # use the audio file as the audio source
            r = sr.Recognizer()
            with sr.AudioFile(sound_file) as source:
                audio = r.record(source)  # read the entire audio file
                self.text_results.append(self.get_text_from_speech(audio))
                self.speaker_results.append(self.get_speaker_from_wav(sound_file))
                self.timestamps.append(self.timestamps[-1] + self.chunk_size) 
            del self.timestamps[-1]
            self.save()

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
        speaker_res = identify_file(BING_KEY, wav_fname, "true", list(self.prof_ids.keys()))
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

    def save(self):
        pickle.dump(demo_pp, open("demo_pp.speemo", "wb"))

    def read(self, f):
        return pickle.load(f)

if __name__ == "__main__":
    dict_id2name= {"e640526c-fd2c-415e-92ae-920f23f6c959":"Jonas",
            "0ba77bb5-d1d8-4f5c-ac7c-c0563c25046c": "Jacek",
            "a1237727-360d-450f-b79f-5abef984dcee": "Jonas"}
    demo_pp = demo_preprocessor("EmoFile.wav", dict_id2name, 4000)
    demo_pp.run()
    print(demo_pp.text_results)
    print(demo_pp.speaker_results)
