# todo: with EasyMP3 without mutagen.mp3
def put_from_name(path):
    import os
    from mutagen.mp3 import EasyMP3 as Emp3
    if path[-1] != '/':
        path += '/'
    try:
        names = filter(lambda x: x.endswith('.mp3'), os.listdir(path))
    except OSError:
        print('Error of path')
    else:
        for name in names:
            track = Emp3(path + name)
            try:
                artist, title = name[0:-4].split(' - ', maxsplit=2)
            except ValueError:
                continue
            else:
                track['title'] = title
                track['artist'] = artist
                track.save()
        print('Завершено')


def clear_albums(path):
    import os
    from mutagen.mp3 import EasyMP3
    if path[-1] != '/':
        path += '/'
    if not os.path.exists(path):
        print("Path error\n")
        return
    files = list(filter(lambda x: x.endswith('.mp3'), os.listdir(path)))
    found = False
    for name in files:
        track = EasyMP3(path + name)
        if not ('album' in track.keys() and '.' in track['album'][0]):
            continue
        found = True
        print(track['album'][0] + ' | y/n')
        key = input()
        if key == 'y':  # Todo get pressed key
            track['album'][0] = ''  # Todo doesn't change
            track.save()
    if not found:
        print('Не найдены')
    print('Завершено')


class TrackTags(object):
    def __init__(self, path):
        from mutagen.mp3 import EasyMP3
        from mutagen.mp3 import MP3
        try:
            self.__EasyMP3 = EasyMP3(path)
            self.__MP3 = MP3(path)
        except FileNotFoundError:
            print('Error path')

    def __get_with_key(self, key):
        if key in self.__EasyMP3.keys():
            return self.__EasyMP3[key]
        return None

    def get_album_title(self):
        return self.__get_with_key('album')

    def get_album_picture(self):
        import re
        for item in list(self.__MP3.keys()):
            if re.match('APIC', item):
                return self.__EasyMP3[item].data
        raise RuntimeError('Обложка не задана')

    def get_artist(self):
        return self.__get_with_key('artist')

    def get_title(self):
        return self.__get_with_key('title')

    def set_album_title(self, album_title):
        from mutagen import id3
        self.__EasyMP3['TALB'] = id3.TALB(encoding=3, text=album_title)
        self.__EasyMP3.save()
        del id3

    def set_picture(self, picture_string):
        from mutagen import id3
        import re

        flag = False
        for item in list(self.__EasyMP3.keys()):
            if re.match('APIC', item):
                self.__EasyMP3.tags.pop(item)
        self.__EasyMP3.tags['APIC:'] = id3.APIC(encoding=3, mime='image/jpeg',
                                                type=3, data=picture_string)
        self.__EasyMP3.save(v1=2)
        del id3

    def set_artist(self, artistName):
        from mutagen import id3
        self.__EasyMP3['TPE1'] = id3.TPE1(encoding=3, text=artistName)
        self.__EasyMP3.save()
        del id3

    def set_title(self, trackTitle):
        from mutagen import id3
        self.__EasyMP3['TIT1'] = id3.TIT1(encoding=3, text=trackTitle)
        self.__EasyMP3.save()
        del id3

    def set_picture_from_last_fm(self):
        xml = self.__get_xml()
        pictureUrl = self.__get_picture_url_from_xml(xml)
        pictureName = self.__get_picture_file(pictureUrl)
        self.__set_picture(pictureName)

    def __get_json(self):
        import requests as rl

        API_KEY = '70578b40668e460c6282ee394e448586'
        URL = 'ws.audioscrobbler.com'
        temp = self.get_title()
        parametersDict = dict(api_key=API_KEY, artist=self.get_artist(),
                              track=temp, method='track.getinfo', format='json')
        try:
            response = rl.get('http://' + URL + '/2.0/', parametersDict)
        except rl.exceptions.RequestException as e:
            print('Ошибка: ' + e.strerror)
        else:
            return response.json()

    def __get_xml(self):
        import requests as rl
        API_KEY = '70578b40668e460c6282ee394e448586'
        URL = 'ws.audioscrobbler.com'
        parametersDict = dict(api_key=API_KEY, artist=self.get_artist(),
                              track=self.get_title(), method='track.getinfo')
        try:
            response = rl.get('http://' + URL + '/2.0/', parametersDict)
        except rl.exceptions.RequestException as e:
            print('Ошибка: ' + e.strerror)
        else:
            return response.text

    def __get_picture_url_from_xml(self, xml):
        from bs4 import BeautifulSoup as bs
        result = bs(xml, 'xml')
        if result.find('image', size='extralarge') != None:
            return result.find('image', size='extralarge').text
        elif result.find('image', size='large') != None:
            return result.find('image', size='large').text
        else:
            return ''

    def __get_picture_file(self, url):
        import urllib as ul
        from PIL import Image

        if url == '':
            return 'gag.jpg'

        temp = 'temp' + url[url.rfind('.'):]
        pictureFile = open(temp, 'wb')
        try:
            pictureStr = ul.request.urlopen(url).read()
        except ul.error.URLError:
            return ''
        else:
            pictureFile.write(pictureStr)
            pictureFile.close()
            pic = Image.open(temp)
            pic.save('temp.jpg')
            return 'temp.jpg'

    def __set_picture(self, fileName):
        if fileName == '':
            return
        try:
            pictureFile = open(fileName, 'rb')
            picture_bytes = pictureFile.read()
        except OSError('Неверное имя файла') as e:
            print(e.strerror)
        else:
            self.set_picture(picture_bytes)
        finally:
            pictureFile.close()
