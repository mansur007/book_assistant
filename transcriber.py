import wave
import speech_recognition as sr
# from torch.autograd import Variable
# from deepspeech.model import DeepSpeech
# from deepspeech.decoder import GreedyDecoder
# import deepspeech.data.data_loader
# from deepspeech import transcribe

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


class DeepSpeech2Transcriber(object):
    def __init__(self, args):
        self.model = DeepSpeech.load_model(args.model_path, cuda=False)
        self.model.eval()

        self.labels = DeepSpeech.get_labels(self.model)
        self.audio_conf = DeepSpeech.get_audio_conf(self.model)
        self.parser = deepspeech.data.data_loader.SpectrogramParser(self.audio_conf, normalize=True)
        self.args = args
        if args.decoder == "beam":
            from deepspeech.decoder import BeamCTCDecoder

            self.decoder = BeamCTCDecoder(self.labels, lm_path=args.lm_path, alpha=args.alpha, beta=args.beta,
                                          cutoff_top_n=args.cutoff_top_n, cutoff_prob=args.cutoff_prob,
                                          beam_width=args.beam_width, num_processes=args.lm_workers)
        else:
            self.decoder = GreedyDecoder(self.labels, blank_index=self.labels.index('_'))

        self.audio_cache = {}

    def transcribe_audio(self, filepath, duration=10, offset=0):
        if filepath not in self.audio_cache:
            self.audio_cache[filepath] = deepspeech.data.data_loader.load_audio(filepath)  # [NumFrames x 1] numpy array

        start_frame = int(offset * self.audio_conf['sample_rate'])
        end_frame = int((offset+duration) * self.audio_conf['sample_rate'])
        audio_data = self.audio_cache[filepath][start_frame:end_frame]
        spect = self.parser.parse_np_audio_data(audio_data).contiguous()
        spect = spect.view(1, 1, spect.size(0), spect.size(1))
        out = self.model(Variable(spect, volatile=True))
        out = out.transpose(0, 1)  # TxNxH
        decoded_output, decoded_offsets = self.decoder.decode(out.data)
        # print(json.dumps(transcribe.decode_results(decoded_output, decoded_offsets)))
        return transcribe.decode_results(decoded_output, decoded_offsets, self.model, self.args)['output'][0]['transcription']


class GoogleCloudTranscriber(object):
    def __init__(self, interval=10):
        self.filepath = None
        self.interval = interval
        self.recognizer = sr.Recognizer()
        # self.recognizer.energy_threshold = 150

    def transcribe_speech(self):
        with sr.Microphone(sample_rate=44100) as source:
            audio = self.recognizer.listen(source)

        try:
            return self.recognizer.recognize_google(audio)
        except LookupError:
            print("Could not understand audio")

    def transcribe_audio(self, filepath, duration=10, offset=0):

        # BING_KEY = "e79428ef2245453aadb919d18003f74b"

        with sr.AudioFile(filepath) as source:
            audio = self.recognizer.record(source, duration, offset)
        try:

            return ("Google Cloud: " + str(self.recognizer.recognize_google(
                audio, language="en-GB",
                show_all=False)))
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