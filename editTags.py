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

        for item in list(self.__EasyMP3.keys()):
            if re.match('APIC', item):
                self.__EasyMP3.tags.pop(item)
        self.__EasyMP3.tags['APIC:'] = id3.APIC(encoding=3, mime='image/jpeg',
                                                type=3, data=picture_string)
        self.__EasyMP3.save(v1=2)
        del id3

    def set_artist(self, artist):
        from mutagen import id3
        self.__EasyMP3['TPE1'] = id3.TPE1(encoding=3, text=artist)
        self.__EasyMP3.save()
        del id3

    def set_title(self, title):
        from mutagen import id3
        self.__EasyMP3['TIT1'] = id3.TIT1(encoding=3, text=title)
        self.__EasyMP3.save()
        del id3

    def set_picture_from_last_fm(self):
        xml = self.__get_xml()
        picture_url = self.__get_picture_url_from_xml(xml)
        picture_name = self.__get_picture_file(picture_url)
        self.__set_picture(picture_name)

    def __get_json(self):
        import requests as rl
        import lastFmData

        temp = self.get_title()
        parameters_dict = {'api_key': lastFmData.API_KEY,
                           'artist': self.get_artist(), 'track': temp,
                           'method': 'track.getinfo', 'format': 'json'}
        try:
            response = rl.get('http://' + lastFmData.URL + '/2.0/',
                              parameters_dict)
        except rl.exceptions.RequestException as e:
            print('Ошибка: ' + e.strerror)
        return response.json()

    def __get_xml(self):
        import requests as rl
        import lastFmData

        parameters_dict = {'api_key': lastFmData.API_KEY,
                           'artist': self.get_artist(),
                           'track': self.get_title(), 'method': 'track.getinfo'}
        try:
            response = rl.get('http://' + lastFmData.URL + '/2.0/',
                              parameters_dict)
        except rl.exceptions.RequestException as e:
            print('Ошибка: ' + e.strerror)
        else:
            return response.text

    @staticmethod
    def __get_picture_url_from_xml(xml):
        from bs4 import BeautifulSoup
        result = BeautifulSoup(xml, 'xml')
        if result.find('image', size='extralarge') is not None:
            return result.find('image', size='extralarge').text
        elif result.find('image', size='large') is not None:
            return result.find('image', size='large').text
        else:
            return ''

    @staticmethod
    def __get_picture_file(url):
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

    def __set_picture(self, file_name):
        if file_name == '':
            return
        try:
            pictureFile = open(file_name, 'rb')
            picture_bytes = pictureFile.read()
        except OSError('Неверное имя файла') as e:
            print(e.strerror)
        else:
            self.set_picture(picture_bytes)
        finally:
            pictureFile.close()
