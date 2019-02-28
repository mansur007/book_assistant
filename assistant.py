import os
from tkinter import *
from tkinter.filedialog import askdirectory
import argparse
import time

import player
import transcriber
import text_processor
import functions

from pocketsphinx import *

import threading
from wakeword_detector import WWDetector

# import wave
# import pydub # open almost any format, slice
# import pyaudio
# maybe import pyglet
# import pygame

parser = argparse.ArgumentParser(description='wakeword detection')
porcupine_root = '/data/soft/Porcupine/'  # will be useful for specifying paths
parser.add_argument('--keyword_file_paths', help='comma-separated absolute paths to keyword files', type=str,
                    default=os.path.join(porcupine_root, 'assistant_linux.ppn'))  # ! default wakeword is "assistant"
parser.add_argument(
    '--library_path',
    help="absolute path to Porcupine's dynamic library", type=str,
    default=os.path.join(porcupine_root, 'lib/linux/x86_64/libpv_porcupine.so'))
parser.add_argument(
    '--model_file_path',
    help='absolute path to model parameter file',
    type=str,
    default=os.path.join(porcupine_root, 'lib/common/porcupine_params.pv'))
parser.add_argument('--sensitivities', help='detection sensitivity [0, 1]', default=0.5)
parser.add_argument('--input_audio_device_index', help='index of input audio device', type=int, default=None)
parser.add_argument(
    '--output_path',
    help='absolute path to where recorded audio will be stored. If not set, it will be bypassed.',
    type=str,
    default=None)
parser.add_argument('--show_audio_devices_info', action='store_true')
wwd_args = parser.parse_args()


TranscriptDuration = 8

PL = player.PlayList()

T = transcriber.GoogleTranscriber()
# T = transcriber.DeepSpeech2Transcriber(args)
D = functions.Dictionary()


def ask_playlist():
    # asks directory of a playlist and makes list of songs from it
    dir = askdirectory()
    os.chdir(dir)

    for file in os.listdir(dir):
        if file.endswith(".wav"):
            e = player.PLEntry(file)
            PL.add(e)
            #print(file)
    return




class GUI(threading.Thread):
    def __init__(self, PL, T, D, TranscriptDuration):
        super().__init__()
        self.PL = PL  # playlist
        self.T = T  # transcriber
        self.D = D  # dictionary
        self.TranscriptDuration = TranscriptDuration
        self.root = Tk()
        self.track_list = Listbox(self.root, selectmode=SINGLE)  # visual representation of playlist
        self.track_list.grid(row=0, rowspan=2)
        for item in PL.entry_list:
            self.track_list.insert(END, item.audio_path)
        self.track_list.selection_set(0)
        self.track_list.activate(0)
        self.prev_button = Button(self.root, text='Prev')
        self.prev_button.grid(row=0, column=1)
        # prev_button.pack(side=LEFT, fill=X)

        self.play_button = Button(self.root, text='Play')
        # play_button.pack(side=LEFT, fill=X)
        self.play_button.grid(row=0, column=2)

        self.stop_button = Button(self.root, text='Stop')
        self.stop_button.grid(row=0, column=3)
        # stop_button.pack(side=LEFT, fill=X)

        self.next_button = Button(self.root, text='Next')
        self.next_button.grid(row=0, column=4)
        # next_button.pack(side=LEFT, fill=X)

        self.pause_button = Button(self.root, text='Pause')
        self.pause_button.grid(row=0, column=5)
        # pause_button.pack(side=BOTTOM, fill=X)

        self.transcribe_button = Button(self.root, text='Transcribe')
        self.transcribe_button.grid(row=1, column=1)
        # transcribe_button.pack(side=LEFT, fill=X)

        self.get_pos_button = Button(self.root, text='Get_Pos')
        self.get_pos_button.grid(row=1, column=2)
        # get_pos_button.pack(side=LEFT, fill=X)

        self.go_to_button = Button(self.root, text='Go_to(time in sec)')
        self.go_to_button.grid(row=1, column=3)
        # go_to_button.pack(side=LEFT, fill=X)

        self.target_time_entry = Entry(self.root)
        self.target_time_entry.grid(row=1, column=4, columnspan=2)

        self.dialogue_box = Text(self.root, wrap=WORD, height=7)
        self.dialogue_box.configure(font=("Times New Roman", 14))
        self.dialogue_box.grid(row=3, columnspan=5)

        self.transcription_box = Text(self.root, wrap=WORD, height=15)
        self.transcription_box.configure(font=("Times New Roman", 14))
        self.transcription_box.grid(row=4, columnspan=5)
        self.transcription_scrollbar = Scrollbar(self.root, orient="vertical", command=self.transcription_box.yview)
        self.transcription_box.configure(yscrollcommand=self.transcription_scrollbar.set)
        self.transcription_scrollbar.grid(row=4, column=6)

        self.show_recent_words_button = Button(self.root, text='Show Recent Words')
        self.show_recent_words_button.grid(row=2, column=3)

        self.speak_button = Button(self.root, text='Voice Command')
        self.speak_button.grid(row=2, column=2)

        self.play_button.bind("<Button-1>", self.play_track)
        self.stop_button.bind("<Button-1>", self.stop_track)
        self.next_button.bind("<Button-1>", self.next_track)
        self.prev_button.bind("<Button-1>", self.prev_track)
        self.pause_button.bind("<Button-1>", self.pause_track)
        self.transcribe_button.bind("<Button-1>", self.transcribe_recent)
        self.get_pos_button.bind("<Button-1>", self.get_pos)
        self.go_to_button.bind("<Button-1>", self.go_to)
        self.speak_button.bind("<Button-1>", self.process_speech)
        self.show_recent_words_button.bind("<Button-1>", self.show_recent_words)

        # making sure that first utterance shows up:
        self.cur_interval_start = -0.001
        self.cur_interval_end = 0

        self.root.after(50, self.update_script)

        self.root.mainloop()

    def play_track(self, event):
        is_unpausing = self.PL.play()
        if is_unpausing is True:
            self.skip_update = True

    def stop_track(self, event):
        self.PL.stop()

    def prev_track(self, event):
        PL.goto_prev()
        self.track_list.selection_clear(0, END)
        self.track_list.selection_set(self.PL.curr_index)
        self.track_list.activate(self.PL.curr_index)

    def next_track(self, event):
        PL.goto_next()
        self.track_list.selection_clear(0, END)
        self.track_list.selection_set(self.PL.curr_index)
        self.track_list.activate(self.PL.curr_index)

    def pause_track(self, event):
        self.PL.pause()

    def transcribe_recent(self, event):
        offset = max(0, self.PL.current_time() - self.TranscriptDuration)
        transcription = self.T.transcribe_audio(self.PL.get_cur_track_path(), self.TranscriptDuration, offset)
        self.dialogue_box.insert(0.2, transcription + "\n\n")

    def process_speech(self, event):
        transcription = self.T.transcribe_mic()
        self.dialogue_box.insert(0.2, "User: {}\n\n".format(transcription))
        parsed_command = text_processor.parse_command(transcription)
        if parsed_command['func'] != 'unknown' and parsed_command['phrase'] == 'it':
            self.dialogue_box.insert(0.2, "assistant could not comprehend the target phrase\n\n")

        elif parsed_command['func'] == 'translate':
            recently_played_words = self.PL.get_recent_words()

            target_word = None
            max_len = 0
            for w in parsed_command['phrase']:
                if len(w) > max_len:
                    target_word = w
                    max_len = len(w)
            target_word = text_processor.find_most_similar_word(target_word, recently_played_words)

            translation_dict = self.D.translate(target_word, 'ru')
            translation = translation_dict['translatedText']
            self.dialogue_box.insert(0.2, "translation of {}: {}\n\n".
                                format(target_word, translation))

        elif parsed_command['func'] == 'define':
            recently_played_words = self.PL.get_recent_words()

            phrase = parsed_command['phrase']
            target_word = None
            max_len = 0
            for w in phrase:
                if len(w) > max_len:
                    target_word = w
                    max_len = len(w)
            target_word = text_processor.find_most_similar_word(target_word, recently_played_words)

            definition = self.D.define(target_word)
            self.dialogue_box.insert(0.2, "definition of {}: {}\n\n".
                                format(target_word, definition))

        print("parsed command: {}\n".format(parsed_command))

    # shows the most recent words from provided transcript
    def show_recent_words(self, event):
        recent_words = self.PL.get_recent_words()
        self.dialogue_box.insert(0.2, ' '.join(recent_words) + "\n\n")
        self.transcription_box.see("end")

    def get_pos(self, event):
        pos = self.PL.current_time()
        print(pos)

    def go_to(self, event):
        target_time = float(self.target_time_entry.get())
        PL.go_to(target_time)

    def update_script(self):
        t = max(PL.current_time(), 0)
        if t > self.cur_interval_end or t < self.cur_interval_start:
            # print("t: {}, cur_interval_start: {}, cur_interval_end: {}".
            #       format(t, cur_interval_start, cur_interval_end))
            # sys.stdout.flush()

            utterance = self.PL.get_utterance(t)
            self.cur_interval_start = utterance['start_time']
            self.cur_interval_end = utterance['end_time']
            self.transcription_box.insert('end', '{}\n\n'.format(utterance['text']))
            self.transcription_box.see('end')

        self.root.after(150, self.update_script)

if __name__ == '__main__':
    ask_playlist()

    if wwd_args.show_audio_devices_info:
        WWDetector.show_audio_devices_info()
    else:
        if not wwd_args.keyword_file_paths:
            raise ValueError('keyword file paths are missing')

        keyword_file_paths = [x.strip() for x in wwd_args.keyword_file_paths.split(',')]

        if isinstance(wwd_args.sensitivities, float):
            sensitivities = [wwd_args.sensitivities] * len(keyword_file_paths)
        else:
            sensitivities = [float(x) for x in wwd_args.sensitivities.split(',')]

        WWDetector(
            library_path=wwd_args.library_path,
            model_file_path=wwd_args.model_file_path,
            keyword_file_paths=keyword_file_paths,
            sensitivities=sensitivities,
            output_path=wwd_args.output_path,
            input_device_index=wwd_args.input_audio_device_index).start()


    # dummy_thread = threading.Thread(target=wakeword_detector.dummy_f)
    # dummy_thread.start()
    gui_thread = GUI(PL, T, D, TranscriptDuration)
    gui_thread.start()

    # # background keyword spotter
    # from pocketsphinx import LiveSpeech
    #
    # speech = LiveSpeech(lm=False, keyphrase='forward', kws_threshold=1e-20)
    # for phrase in speech:
    #     out = phrase.segments(detailed=True)
    #     print(out)


    # t = threading.Thread(target=wakeword_detector.dummy_f)
    # t.start()

    # pocketsphinx_dir = os.path.dirname(pocketsphinx.__file__)
    # model_dir = os.path.join(pocketsphinx_dir, 'model')
    # config = pocketsphinx.Decoder.default_config()
    # config.set_string('-hmm', os.path.join(model_dir, 'en-us'))
    # config.set_string('-keyphrase', 'stop')
    # config.set_string('-dict', os.path.join(model_dir, 'cmudict-en-us.dict'))
    # config.set_float('-kws_threshold', 1e+20)
    #
    # p = pyaudio.PyAudio()
    #
    # stream = p.open(format=pyaudio.paInt16, channels=1, rate=16000, input=True, frames_per_buffer=20480)
    # stream.start_stream()
    #
    # decoder = Decoder(config)
    # decoder.start_utt()
    # buf = stream.read(1024)
    # if buf:
    #     decoder.process_raw(buf)
    # else:
    #     break


