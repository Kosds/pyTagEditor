import editTags as eT
import os

path = "/home/daniil/music_for_testing/"
names = filter(lambda x: x.endswith('.mp3'), os.listdir(path))
for name in names:
    track = eT.TrackTags(path + name)
    track.set_picture_from_last_fm()
