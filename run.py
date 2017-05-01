import editTags as eT
import os

print('path: ')
path = input()
if os.path.exists(path):
    eT.put_from_name(path)
