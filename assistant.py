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
import wakeword_detector

# import wave
# import pydub # open almost any format, slice
# import pyaudio
# maybe import pyglet
# import pygame

parser = argparse.ArgumentParser(description='DeepSpeech2 transcription')
parser.add_argument('--model_path', default='deepspeech/models/librispeech_pretrained.pth',
                    help='Path to model file created by training')
parser.add_argument('--decoder', default="greedy", choices=["greedy", "beam"], type=str, help="Decoder to use")
parser.add_argument('--offsets', dest='offsets', action='store_true', help='Returns time offset information')
beam_args = parser.add_argument_group("Beam Decode Options", "Configurations options for the CTC Beam Search decoder")
beam_args.add_argument('--top_paths', default=1, type=int, help='number of beams to return')
beam_args.add_argument('--beam_width', default=10, type=int, help='Beam width to use')
beam_args.add_argument('--lm_path', default='deepspeech/lm/3-gram.pruned.1e-7.arpa', type=str,
                       help='Path to an (optional) kenlm language model for use with beam search (req\'d with trie)')
beam_args.add_argument('--alpha', default=0.8, type=float, help='Language model weight')
beam_args.add_argument('--beta', default=1, type=float, help='Language model word bonus (all words)')
beam_args.add_argument('--cutoff_top_n', default=40, type=int,
                       help='Cutoff number in pruning, only top cutoff_top_n characters with highest probs in '
                            'vocabulary will be used in beam search, default 40.')
beam_args.add_argument('--cutoff_prob', default=1.0, type=float,
                       help='Cutoff probability in pruning,default 1.0, no pruning.')
beam_args.add_argument('--lm_workers', default=1, type=int, help='Number of LM processes to use')
args = parser.parse_args()


TranscriptDuration = 8

PL = player.PlayList()


def update_script():
    global cur_interval_start, cur_interval_end
    t = max(PL.current_time(), 0)
    if t > cur_interval_end or t < cur_interval_start:
        # print("t: {}, cur_interval_start: {}, cur_interval_end: {}".
        #       format(t, cur_interval_start, cur_interval_end))
        # sys.stdout.flush()

        utterance = PL.get_utterance(t)
        cur_interval_start = utterance['start_time']
        cur_interval_end = utterance['end_time']
        transcription_box.insert('end', '{}\n\n'.format(utterance['text']))
        transcription_box.see('end')

    root.after(150, update_script)


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


def play_track(event):
    is_unpausing = PL.play()
    if is_unpausing is True:
        skip_update = True


def stop_track(event):
    PL.stop()


def prev_track(event):
    PL.goto_prev()
    track_list.selection_clear(0, END)
    track_list.selection_set(PL.curr_index)
    track_list.activate(PL.curr_index)


def next_track(event):
    PL.goto_next()
    track_list.selection_clear(0, END)
    track_list.selection_set(PL.curr_index)
    track_list.activate(PL.curr_index)

def pause_track(event):
    PL.pause()


def transcribe_recent(event):
    offset = max(0, PL.current_time() - TranscriptDuration)
    transcription = T.transcribe_audio(PL.get_cur_track_path(), TranscriptDuration, offset)
    dialogue_box.insert(0.2, transcription+"\n\n")


def process_speech(event):
    transcription = T.transcribe_mic()
    dialogue_box.insert(0.2, "User: {}\n\n".format(transcription))
    parsed_command = text_processor.parse_command(transcription)
    if parsed_command['func'] != 'unknown' and parsed_command['phrase'] == 'it':
        dialogue_box.insert(0.2, "assistant could not comprehend the target phrase\n\n")

    elif parsed_command['func'] == 'translate':
        recently_played_words = PL.get_recent_words()

        target_word = None
        max_len = 0
        for w in parsed_command['phrase']:
            if len(w) > max_len:
                target_word = w
                max_len = len(w)
        target_word = text_processor.find_most_similar_word(target_word, recently_played_words)

        translation_dict = D.translate(target_word, 'ru')
        translation = translation_dict['translatedText']
        dialogue_box.insert(0.2, "translation of {}: {}\n\n".
                            format(target_word, translation))

    elif parsed_command['func'] == 'define':
        recently_played_words = PL.get_recent_words()

        phrase = parsed_command['phrase']
        target_word = None
        max_len = 0
        for w in phrase:
            if len(w) > max_len:
                target_word = w
                max_len = len(w)
        target_word = text_processor.find_most_similar_word(target_word, recently_played_words)

        definition = D.define(target_word)
        dialogue_box.insert(0.2, "definition of {}: {}\n\n".
                            format(target_word, definition))

    print("parsed command: {}\n".format(parsed_command))


# shows the most recent words from provided transcript
def show_recent_words(event):
    recent_words = PL.get_recent_words()
    dialogue_box.insert(0.2, ' '.join(recent_words) + "\n\n")
    transcription_box.see("end")


def get_pos(event):
    pos = PL.current_time()
    print(pos)


def go_to(event):
    target_time = float(target_time_entry.get())
    PL.go_to(target_time)

if __name__ == '__main__':
    ask_playlist()
    # # background keyword spotter
    # from pocketsphinx import LiveSpeech
    #
    # speech = LiveSpeech(lm=False, keyphrase='forward', kws_threshold=1e-20)
    # for phrase in speech:
    #     out = phrase.segments(detailed=True)
    #     print(out)
    #### GUI #######################################################
    root = Tk()
    track_list = Listbox(root, selectmode=SINGLE)
    track_list.grid(row=0, rowspan=2)
    for item in PL.entry_list:
        track_list.insert(END, item.audio_path)
    track_list.selection_set(0)
    track_list.activate(0)

    prev_button = Button(root, text='Prev')
    prev_button.grid(row=0, column=1)
    # prev_button.pack(side=LEFT, fill=X)

    play_button = Button(root, text='Play')
    # play_button.pack(side=LEFT, fill=X)
    play_button.grid(row=0, column=2)

    stop_button = Button(root, text='Stop')
    stop_button.grid(row=0, column=3)
    # stop_button.pack(side=LEFT, fill=X)

    next_button = Button(root, text='Next')
    next_button.grid(row=0, column=4)
    # next_button.pack(side=LEFT, fill=X)

    pause_button = Button(root, text='Pause')
    pause_button.grid(row=0, column=5)
    # pause_button.pack(side=BOTTOM, fill=X)

    transcribe_button = Button(root, text='Transcribe')
    transcribe_button.grid(row=1, column=1)
    # transcribe_button.pack(side=LEFT, fill=X)

    get_pos_button = Button(root, text='Get_Pos')
    get_pos_button.grid(row=1, column=2)
    # get_pos_button.pack(side=LEFT, fill=X)

    go_to_button = Button(root, text='Go_to(time in sec)')
    go_to_button.grid(row=1, column=3)
    # go_to_button.pack(side=LEFT, fill=X)

    target_time_entry = Entry(root)
    target_time_entry.grid(row=1, column=4, columnspan=2)

    dialogue_box = Text(root, wrap=WORD, height=7)
    dialogue_box.configure(font=("Times New Roman", 14))
    dialogue_box.grid(row=3, columnspan=5)

    transcription_box = Text(root, wrap=WORD, height=15)
    transcription_box.configure(font=("Times New Roman", 14))
    transcription_box.grid(row=4, columnspan=5)
    transcription_scrollbar = Scrollbar(root, orient="vertical", command=transcription_box.yview)
    transcription_box.configure(yscrollcommand=transcription_scrollbar.set)
    transcription_scrollbar.grid(row=4, column=6)

    show_recent_words_button = Button(root, text='Show Recent Words')
    show_recent_words_button.grid(row=2, column=3)

    speak_button = Button(root, text='Voice Command')
    speak_button.grid(row=2, column=2)

    play_button.bind("<Button-1>", play_track)
    stop_button.bind("<Button-1>", stop_track)
    next_button.bind("<Button-1>", next_track)
    prev_button.bind("<Button-1>", prev_track)
    pause_button.bind("<Button-1>", pause_track)
    transcribe_button.bind("<Button-1>", transcribe_recent)
    get_pos_button.bind("<Button-1>", get_pos)
    go_to_button.bind("<Button-1>", go_to)
    speak_button.bind("<Button-1>", process_speech)
    show_recent_words_button.bind("<Button-1>", show_recent_words)

    # cur_interval_start = PL.get_cur_track_entry().utt_intervals[0, 0]
    # cur_interval_end = PL.get_cur_track_entry().utt_intervals[0, 1]
    # making sure that first utterance shows up:
    cur_interval_start = -0.001
    cur_interval_end = 0

    root.after(50, update_script)
    root.mainloop()
    #################################################################

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


