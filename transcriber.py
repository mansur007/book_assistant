import wave
import numpy as np
import matplotlib.pyplot as plt
import speech_recognition as sr


class DeepSpeech2Transcriber(object):
    def __init__(self, model_path):
        pass


class GoogleCloudTranscriber(object):
    def __init__(self, interval=10):
        self.filepath = None
        self.interval = interval
        self.recognizer = sr.Recognizer()
        # self.recognizer.energy_threshold = 150

    def transcribe_audio(self, filepath, duration=10, offset=0):
        GOOGLE_CLOUD_SPEECH_CREDENTIALS = r"""
                    {
                      "type": "service_account",
                      "project_id": "my-project-1518932773455",
                      "private_key_id": "0f95b3cd63271d6c7ae84c85226797e63c0b9340",
                      "private_key": "-----BEGIN PRIVATE KEY-----\nMIIEvQIBADANBgkqhkiG9w0BAQEFAASCBKcwggSjAgEAAoIBAQDfCztSo2mgjlnA\nM9ROsKwtMyN0MkDadwMKD0VgX9uq2d8/FwFuCLfky+uBz7e7MPmAS80ikY/90KyC\n42cEZJZHmDMB8vvTVD/PYTYC0bvLJX4REyUMAhjnb8zFhfyMbQs9AVXRZkk7s54q\nH38yGPCpSUBHHmQvvo+Z5eXNDLpwYt/rGqyos7fjY7/UYsVX1JMQYr4gZ/7uT7N+\n5de0jHM5yFmUkQCt2x+Icih27HWZCcNVswXE5YOAs09MTcX0eNTwGn8HbwrBKBiY\nae/HNiM0NWXqf+r4qAv8Q8GrypkAd4oUW+pa5o4CqEt+dKdmcfK0dX7CIaNqB8sK\nLjw/XR6tAgMBAAECggEAM/ck8iL6iBrCVGJ+83p8EufYOck/jOavgZd/PW33+v1Z\n4xQUFDPZzGeqTgs8LlPBvZ9rgsNRPfxxROmAZeidjr6qG6kl/N2jJEjs0YlV7IWm\nsom4VuziKoHEvrxx07HQLX1zJh9jrpIxpnTCKMTgxUA4xpkRFIKcaGnEuZpekbI4\nKzO1Y9KoAqZsBnxFmIc0bDrzLLR/Sqw7XTYhwuq/jgjSOeLsjAa2awf70n+SElqL\ncKv7N/O7Z6loZMiW/GFpoMia2a+L33+LsiElHHL716oujfTmlfovTA03T06hoqhj\nj4k7U8ofLV8mTgnmraqsbYygq+1be7RVUUQFoVRuYQKBgQD6cVl2bZObV1spNxr3\nuIRBoq7pGy7E9WxH/PK+C/6k3V+ReMI7m1l+K9pTJGoJfLX4Qd/T+pSxhOfhTEyE\nsL5P3K/mTvZmYUgDBda1GvdzOhNEN7P0cWLJ+42HZ0DalE2iofzrrSuhca/OUKiA\n2e+2c9UcLZ9/XGCZmFsO32z4mQKBgQDj/j3ftaJAgUM1LAVs3n3JzRP2J+JlOcOU\nqSPjxYzxcGejILNqzhR56mSmL1yBPLEu7p06AbpoEPCQwLJf8mPbMxESgQCwU/Kb\ngTmYGYpytAjHHAMypz9EjBiA+ll5ujWAo5DkikM3JmI8z6LcVUJFgOgKC91xCrBH\nqpJ2VaA/NQKBgC8lAVNS41N9yVJj5ja1zGfSqRyGmnJHRP/0NPnjpicA6UmoMuAn\nqVwgAzRdiXyJtnOqaukrpawZOdFmnIzp/JlqEM7JFIdHTtgK1FU5Y1WUnCXeWojs\ng01Ehmrz2/iJrGeuGL+A1NLKZO7wrhe7bu2otnhcekbua9zeGl4dXxUZAoGBAL4f\nVoOGGL6HzH67re6CfwzYikvcKKvXBqSig34+T/FKlfHvpA5tuZ+M+c+ncRGIhgyo\nCM7FgCel8KYVOupN3D1/kT4H+4YPCyHoGhofOle6kBNR5czIsTa9SPXNTu32fQU/\n4OTj83c69/LUB3CLXI9PFrDCAjBxBF1O/YHWl6H9AoGAcWJZNH93DDfmmrtWWJJE\n+Ix0oy9n4TnZ1jhQn2XJgL1/DOlnBSxx9jrAR8aHGifZd1p+BzEagod461h1aGsp\nsM8JAuKnh1sDf9B1IZxnab5kan0X6TllR+vy4vS5L6eDChRG/eyC/i17GzCcDG0u\nOpvG1iHFwz8ea7nWhpJlehg=\n-----END PRIVATE KEY-----\n",
                      "client_email": "starting-account-ily8bej1fmj6@my-project-1518932773455.iam.gserviceaccount.com",
                      "client_id": "110451015820238953502",
                      "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                      "token_uri": "https://accounts.google.com/o/oauth2/token",
                      "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
                      "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/starting-account-ily8bej1fmj6%40my-project-1518932773455.iam.gserviceaccount.com"
                    }
                    """
        # BING_KEY = "e79428ef2245453aadb919d18003f74b"

#         context_phrase = """IMAGINE that you are a teacher of Roman history and the Latin language, anxious to
# impart your enthusiasm for the ancient world - for the elegiacs of Ovid and the odes of Horace, the
# sinewy economy of Latin grammar as exhibited in the oratory of Cicero, the strategic niceties of the
# Punic Wars, the generalship of Julius Caesar and the voluptuous excesses of the later emperors.
# That's a big undertaking and it takes time, concentration, dedication. Yet you find your precious
# time continually preyed upon, and your class's attention distracted, by a baying pack of ignoramuses
# (as a Latin scholar you would know better than to say 'ignorami') who, with strong political and
# especially financial support, scurry about tirelessly attempting to persuade your unfortunate pupils
# that the Romans never existed. There never was a Roman Empire. The entire world came into
# existence only just beyond living memory. Spanish, Italian, French, Portuguese, Catalan, Occitan,
# Romansh: all these languages and their constituent dialects sprang spontaneously and separately
# into being, and owe nothing to any predecessor such as Latin. Instead of devoting your full attention
# to the noble vocation of classical scholar and teacher, you are forced to divert your time and energy
# to a rearguard defence of the proposition that the Romans existed at all: a defence against an
# exhibition of ignorant prejudice that would make you weep if you weren't too busy fighting it.""".split(" ")


        with sr.AudioFile(filepath) as source:
            audio = self.recognizer.record(source, duration, offset)
        try:

            return ("Google Cloud: " + str(self.recognizer.recognize_google_cloud(
                audio, credentials_json=GOOGLE_CLOUD_SPEECH_CREDENTIALS, language="en-GB",
                show_all=False, )))
                # preferred_phrases=context_phrase)))

            # print("Microsoft Bing: " + self.recognizer.recognize_bing(audio, key=BING_KEY))
            #print("Sphinx: " + self.recognizer.recognize_sphinx(audio))
        except sr.UnknownValueError:
            return ("Could not understand audio")
        except sr.RequestError as e:
            return ("Error; {0}".format(e))

    def plot_recent_signal(self, filepath, start=0):  # wrong name, this function was used for debugging
        if self.filepath != filepath:
            self.filepath = filepath
            self.wav_reader = wave.open(filepath, 'r')
        frmps = self.wav_reader.getframerate()
        print(self.wav_reader.getparams())

        signal = self.wav_reader.readframes(self.interval*frmps)
        print(type(signal))
        # print(signal)


        # plt.plot(signal)
        # plt.show()