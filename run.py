import editTags as eT
import os
import time
import threading

are_processed = False

def print_dots():
    POINTS_LIMIT = 5
    while are_processed:
        for i in range(POINTS_LIMIT):
            print(".", sep=" ", flush=True, end=" ")
            time.sleep(0.5)
        os.system("clear")
        time.sleep(0.5)
    print("Done!")

dots_printer = threading.Thread(target=print_dots)
path = "/home/daniil/music_for_testing/"
names = filter(lambda x: x.endswith('.mp3'), os.listdir(path))
are_processed = True
dots_printer.start()
for name in names:
    track = eT.TrackTags(path + name)
    track.set_album_from_last_fm()
    time.sleep(1)
are_processed = False
dots_printer.join()

