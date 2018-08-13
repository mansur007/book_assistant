from pygame import *
import numpy as np
import sys

class PLEntry:
    def __init__(self, audio_path):
        self.audio_path = audio_path
        wmap_path = audio_path[:-3]+'wmap.aud'
        uttmap_path = audio_path[:-3]+'uttmap.aud'
        self.w_intervals = np.genfromtxt(wmap_path, delimiter='\t', usecols=(0, 1), encoding='utf8')
        self.utt_intervals = np.genfromtxt(uttmap_path, delimiter='\t', usecols=(0, 1), encoding='utf8')
        self.words = np.genfromtxt(wmap_path, dtype='str', delimiter='\t', usecols=2, encoding='utf8')
        self.utterances = np.genfromtxt(uttmap_path, dtype='str', delimiter='\t', usecols=2, encoding='utf8')
        self.is_paused = False
        self.pause_time = None  # needed for unpausing, otherwise hard to get correct position of a track,
                                # that's probably pygame issue(?)


class PlayList:
    def __init__(self):
        self.entry_list = []
        self.curr_index = 0  # points to a current entry
        # mixer.init(frequency=44100)
        mixer.init(frequency=16000)

    def is_paused(self):
        return self.get_cur_track_entry().is_paused

    def get_cur_track_entry(self):
        return self.entry_list[self.curr_index]

    def get_cur_track_path(self):
        return self.entry_list[self.curr_index].audio_path

    def add(self, entry):
        self.entry_list.append(entry)

    def play(self, target_time=None):
        # returns True when unpausing, false otherwise
        if target_time is not None:
            print("target time:", target_time)
            mixer.music.play(start=target_time)
            return False
        elif self.entry_list[self.curr_index].is_paused:
            print("unpause...")
            self.entry_list[self.curr_index].is_paused = False
            mixer.music.unpause()
            return True
        elif mixer.music.get_busy():
            print("busy...")
            return False
        else:
            audio_path = self.entry_list[self.curr_index].audio_path
            mixer.music.load(audio_path)
            mixer.music.play()
            return False

    def stop(self):
        print("stop")
        mixer.music.pause()  # to stop position from being incremented
        self.entry_list[self.curr_index].is_paused = False
        mixer.music.stop()

    def pause(self):
        print("pause")
        entry = self.get_cur_track_entry()
        entry.pause_time = mixer.music.get_pos()/1000
        self.entry_list[self.curr_index].is_paused = True
        mixer.music.pause()

    def current_time(self):
        if not self.get_cur_track_entry().is_paused and self.get_cur_track_entry().pause_time is not None:
            t = self.get_cur_track_entry().pause_time
            self.get_cur_track_entry().pause_time = None
            return t
        else:
            return mixer.music.get_pos()/1000

    def go_to(self, target_time):
        self.stop()
        mixer.music.set_pos(target_time)
        self.play()

    def goto_prev(self):
        if self.curr_index == 0:
            self.curr_index = len(self.entry_list) - 1
        else:
            self.curr_index -= 1

    def goto_next(self):
        if self.curr_index == (len(self.entry_list) - 1):
            self.curr_index = 0
        else:
            self.curr_index += 1

    def get_utterance(self, t):
        utterances = self.get_cur_track_entry().utterances
        utt_intervals = self.get_cur_track_entry().utt_intervals
        cur_utterance = np.asscalar(utterances[(utt_intervals[:, 0] <= t) & (utt_intervals[:, 1] >= t)])
        cur_utt_interval = utt_intervals[(utt_intervals[:, 0] <= t) & (utt_intervals[:, 1] >= t)]
        cur_utt_interval = np.reshape(cur_utt_interval, -1)

        # print(cur_utterance)
        # print(cur_utt_interval)
        sys.stdout.flush()
        return {'text': cur_utterance,
                'start_time': cur_utt_interval[0],
                'end_time': cur_utt_interval[1]}

    def get_recent_words(self, duration=10):
        cur_time = self.current_time()

        cur_track_entry = self.get_cur_track_entry()
        w_intervals = cur_track_entry.w_intervals
        words = cur_track_entry.words

        start_time = max(cur_time - duration, 0)
        end_time = min(cur_time, w_intervals[-1][1])

        recent_words = words[(w_intervals[:, 0] >= start_time) & (w_intervals[:, 1] <= end_time)]
        return list(recent_words)