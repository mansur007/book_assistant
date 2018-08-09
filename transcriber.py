import wave
import speech_recognition as sr
from torch.autograd import Variable
from deepspeech.model import DeepSpeech
from deepspeech.decoder import GreedyDecoder
import deepspeech.data.data_loader
from deepspeech import transcribe


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


class GoogleTranscriber(object):
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