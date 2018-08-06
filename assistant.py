import os
from tkinter import *
from tkinter.filedialog import askdirectory
import argparse
import numpy as np

import player
import transcriber

# import wave
# import pydub # open almost any format, slice
# import pyaudio
# maybe import pyglet
# import pygame

parser = argparse.ArgumentParser(description='DeepSpeech2 transcription')
parser.add_argument('--model_path', default='deepspeech/models/librispeech_pretrained.pth',
                    help='Path to model file created by training')
parser.add_argument('--decoder', default="beam", choices=["greedy", "beam"], type=str, help="Decoder to use")
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


TranscriptDuration = 15

PL = player.PlayList()
T = transcriber.GoogleCloudTranscriber()
# T = transcriber.DeepSpeech2Transcriber(args)

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
    transcription_box.insert(0.2, "\n"+transcription+"\n")

def transcribe_speech(event):
    transcription = T.transcribe_speech()
    transcription_box.insert(0.2, "\n" + transcription + "\n")

# shows 20 seconds from true transcript, which are nearest to current time
def show_transcript(event):
    cur_time = PL.current_time()

    cur_track_entry = PL.get_cur_track_entry()
    intervals = cur_track_entry.intervals
    words = cur_track_entry.words

    start_time = max(cur_time - 10, 0)
    end_time = min(cur_time + 10, intervals[-1][1])

    transcript = words[(intervals[:, 0] >= start_time) & (intervals[:, 1] <= end_time)]

    transcription_box.insert(0.2, "\ngiven script: " + ' '.join(transcript) + "\n")

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

    transcription_box = Text(root, wrap=WORD)
    transcription_box.configure(font=("Times New Roman", 14))
    transcription_box.grid(row=3, columnspan=5)

    show_transcript_button = Button(root, text='Show Transcript')
    show_transcript_button.grid(row=2, column=3)

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
    show_transcript_button.bind("<Button-1>", show_transcript)

    root.mainloop()
    #################################################################