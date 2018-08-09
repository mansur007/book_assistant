import os
from tkinter import *
from tkinter.filedialog import askdirectory
import argparse
import time

import player
import transcriber
import text_processor
import functions

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
        utterance = PL.get_utterance(t)
        transcription_box.insert('end', '{}\n\n'.format(utterance['text']))
        transcription_box.see('end')
        cur_interval_start = utterance['start_time']
        cur_interval_end = utterance['end_time']
    root.after(10, update_script)


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
    PL.play()


def stop_track(event):
    PL.stop()


def prev_track(event):
    PL.goto_prev()


def next_track(event):
    PL.goto_next()


def pause_track(event):
    PL.pause()


def transcribe_recent(event):
    offset = max(0, PL.current_time() - TranscriptDuration)
    transcription = T.transcribe_audio(PL.get_cur_track_path(), TranscriptDuration, offset)
    dialogue_box.insert(0.2, transcription+"\n\n")


def transcribe_speech(event):
    transcription = T.transcribe_speech()
    dialogue_box.insert(0.2, "User: {}\n\n".format(transcription))
    parsed_command = text_processor.parse_command(transcription)
    if parsed_command['func'] == 'translate':
        translation = D.translate(parsed_command['phrase'], 'ru')
        dialogue_box.insert(0.2, "translation of {}: {}\n\n".
                            format(parsed_command['phrase'][0], translation[0]['translatedText']))

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

    #### GUI #######################################################
    root = Tk()
    listbox = Listbox(root)
    listbox.grid(row=0, rowspan=2)
    for item in PL.entry_list:
        listbox.insert(0, item.audio_path)

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
    speak_button.bind("<Button-1>", transcribe_speech)
    show_recent_words_button.bind("<Button-1>", show_recent_words)

    # cur_interval_start = PL.get_cur_track_entry().utt_intervals[0, 0]
    # cur_interval_end = PL.get_cur_track_entry().utt_intervals[0, 1]
    # making sure that first utterance shows up:
    cur_interval_start = -0.001
    cur_interval_end = 0

    root.after(10, update_script)
    root.mainloop()
    #################################################################