import os
from tkinter.filedialog import askdirectory
import argparse

import player
import transcriber
import dictionary

from wakeword_detector import WWDetector
import tkinter as tk
from gui import GUI


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


def ask_playlist(pl):
    # asks directory of a playlist and makes list of songs from it;
    # pl is a player.Playlist instance

    # following 2 lines are for avoiding appearance of the root window that is not used
    root = tk.Tk()
    root.withdraw()

    directory = askdirectory()
    os.chdir(directory)

    for file in os.listdir(directory):
        if file.endswith(".wav"):
            e = player.PLEntry(file)
            pl.add(e)
    return


if __name__ == '__main__':
    TranscriptDuration = 8
    PL = player.PlayList()
    T = transcriber.GoogleTranscriber()
    D = dictionary.Dictionary()
    ask_playlist(PL)

    if not wwd_args.keyword_file_paths:
        raise ValueError('keyword file paths are missing')

    keyword_file_paths = [x.strip() for x in wwd_args.keyword_file_paths.split(',')]

    if isinstance(wwd_args.sensitivities, float):
        sensitivities = [wwd_args.sensitivities] * len(keyword_file_paths)
    else:
        sensitivities = [float(x) for x in wwd_args.sensitivities.split(',')]

    gui_thread = GUI(PL, T, D, TranscriptDuration)

    WWDetector(
        gui=gui_thread,
        library_path=wwd_args.library_path,
        model_file_path=wwd_args.model_file_path,
        keyword_file_paths=keyword_file_paths,
        sensitivities=sensitivities,
        output_path=wwd_args.output_path,
        input_device_index=wwd_args.input_audio_device_index).start()

    gui_thread.root.mainloop()
    gui_thread.start()

