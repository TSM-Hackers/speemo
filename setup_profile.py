import speech_recognition as sr
from os import path
import os
import sys
sys.path.append('third_party/Identification')
from CreateProfile import create_profile
from EnrollProfile import enroll_profile
from pydub import AudioSegment
from pydub.utils import make_chunks
import pickle
import wx
from wx.lib.pubsub import pub
import thumbnails_toolkit as tk

dict_id2name= {"e640526c-fd2c-415e-92ae-920f23f6c959":"Jonas",
        "0ba77bb5-d1d8-4f5c-ac7c-c0563c25046c": "Jacek",
        "a1237727-360d-450f-b79f-5abef984dcee": "Eduardo"}

class ProfileCreator:
    def __init__(self):
        self.locale = 'en-us'
        self.bing_key = "dfe8481d30814fa296829b9e6b3d6842"
        thumb = tk.get_thumbnail()
        if thumb is not None:
            # Load the original image, fetched from the URL
            self.thumb_fname = "photo_thumbnail.jpg"
            with open(self.thumb_fname, 'wb') as f:
                f.write(thumb)
            print("showing image")
    
    def create(self):
        return create_profile(self.bing_key, self.locale)


class ProfileEnroller:
    def __init__(self, enrollment_file_path):
        self.enrollment_file_path = enrollment_file_path
        self.profile_creator = ProfileCreator()
        self.profile_id = self.profile_creator.create()

    def enroll(self):
        enroll_profile(self.profile_creator.bing_key, self.profile_id, self.enrollment_file_path, "false")
        
    def save(self, filepath):
        pickle.dump(self, open(filepath, "wb"))

    @staticmethod
    def read(filepath):
        return pickle.load(open(filepath, "rb"))

if __name__ == "__main__":
    profile_enroller = ProfileEnroller("JacekEnrollment.wav")
    profile_enroller.enroll()
