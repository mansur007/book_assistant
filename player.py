from pygame import *



class Speaker:
    def __init__(self):
        mixer.init(frequency=16000)
        self.isPaused = False

    def play(self, path, target_time = None):
        print(mixer.music.get_pos())
        if target_time is not None:
            mixer.music.play(start=target_time)
        elif self.isPaused:
            mixer.music.unpause()
            self.isPaused = False
        elif mixer.music.get_busy():
            return self
        else:
            mixer.music.load(path)
            mixer.music.play()

    def stop(self):
        mixer.music.stop()

    def pause(self):
        mixer.music.pause()
        self.isPaused = True

    def current_time(self):
        return mixer.music.get_pos()/1000

    def go_to(self, target_time):
        mixer.music.set_pos(target_time)
