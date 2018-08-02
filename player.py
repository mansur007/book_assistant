from pygame import *
#import mutagen.MP3


class PLEntry:
    def __init__(self, path):
        self.path = path
        self.time = 0
        self.is_paused = False


class PlayList:
    def __init__(self):
        self.raw_list = []
        self.curr_index = 0  # points to a current entry
        self.len = 0
        # mixer.init(frequency=44100)
        mixer.init(frequency=16000)

    def get_cur_track_path(self):
        return self.raw_list[self.curr_index].path

    def add(self, entry):
        self.raw_list.append(entry)
        self.len += 1

    def play(self, target_time=None):
        #print(mixer.music.get_pos())
        if target_time is not None:
            print("target time:", target_time)
            mixer.music.play(start=target_time)
        elif self.raw_list[self.curr_index].is_paused:
            print("unpause...")
            self.raw_list[self.curr_index].is_paused = False
            mixer.music.unpause()
        elif mixer.music.get_busy():
            print("busy...")
            return self
        else:
            path = self.raw_list[self.curr_index].path
            mixer.music.load(path)
            mixer.music.play()

    def stop(self):
        print("stop")
        self.raw_list[self.curr_index].is_paused = False
        mixer.music.stop()

    def pause(self):
        print("pause")
        self.raw_list[self.curr_index].is_paused = True
        mixer.music.pause()

    def current_time(self):
        return mixer.music.get_pos()/1000

    def go_to(self, target_time):
        self.stop()
        mixer.music.set_pos(target_time)
        self.play()

    def goto_prev(self):
        if self.curr_index == 0:
            self.curr_index = len(self.raw_list) - 1
        else:
            self.curr_index -= 1

    def goto_next(self):
        if self.curr_index == (len(self.raw_list) - 1):
            self.curr_index = 0
        else:
            self.curr_index += 1
