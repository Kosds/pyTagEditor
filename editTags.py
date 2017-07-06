def put_from_name(path):
    import os
    from mutagen.mp3 import EasyMP3 as Emp3
    if path[-1] != '/':
        path += '/'
    if path[0] == "~":
        path = os.path.expanduser(path)
    path = os.path.abspath(path)
    if not os.path.exists(path):
        print("Path error")
        return
    wrong_names = []
    names = filter(lambda x: x.endswith('.mp3'), os.listdir(path))
    for name in names:
        track = Emp3(path + name)
        try:
            artist, title = name[0:-4].split(' - ', maxsplit=2)
        except ValueError:
            wrong_names.append(name)
            continue
        track['title'] = title
        track['artist'] = artist
        track.save()
    print('Завершено')
    if len(wrong_names) != 0:
        print("Ошибочные имена файлов: ")
        for name in wrong_names:
            print(name)


def clear_albums(path):
    import os
    from mutagen.mp3 import EasyMP3
    if path[-1] != '/':
        path += '/'
    if path[0] == "~":
        path = os.path.expanduser(path)
    path = os.path.abspath(path)
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
        if key == 'y':
            track['album'] = ""
            track.save()
    if not found:
        print('Не найдены')
    print('Завершено')


class TrackTags(object):
    def __init__(self, path):
        from mutagen.mp3 import EasyMP3
        import os
        if path[0] == "~":
            path = os.path.expanduser(path)
        path = os.path.abspath(path)
        if not os.path.exists(path):
            raise FileNotFoundError("Path error")
        self.__EasyMP3 = EasyMP3(path)
        self.__path = path

    def __get_with_key(self, key):
        if key in self.__EasyMP3.keys():
            return self.__EasyMP3[key]
        return None

    def get_album(self):
        return self.__get_with_key("album")

    def get_picture(self):
        import re
        from mutagen.mp3 import MP3
        track = MP3(self.__path)
        for tag_type in list(track.keys()):
            if re.match('APIC', tag_type):
                return track[tag_type].data
        return None

    def get_artist(self):
        return self.__get_with_key("artist")

    def get_title(self):
        return self.__get_with_key("title")

    def set_album(self, album_title):
        self.__EasyMP3["album"] = album_title
        self.__EasyMP3.save()

    def set_picture(self, picture_bytes):
        import mutagen
        from mutagen.mp3 import MP3
        import re
        track = MP3(self.__path)
        for tag_type in list(track.keys()):
            if re.match('APIC', tag_type):
                track.tags.pop(tag_type)
        pic = mutagen.id3.APIC(encoding=3, mime='image/jpeg', type=3, data=picture_bytes)
        track.tags['APIC:'] = pic
        track.save(v1=2)

    def set_artist(self, artist):
        self.__EasyMP3["artist"] = artist
        self.__EasyMP3.save()

    def set_title(self, title):
        self.__EasyMP3["title"] = title
        self.__EasyMP3.save()

    def set_picture_from_last_fm(self):
        import os
        xml = self.__get_xml()
        picture_url = self.__get_picture_url_from_xml(xml)
        picture_file = self.__get_picture_file(picture_url)
        self.__set_picture(picture_file)
        os.unlink(picture_file)

    def set_album_from_last_fm(self):
        from bs4 import BeautifulSoup
        xml = self.__get_xml()
        parser = BeautifulSoup(xml, "xml")
        album = parser.find("title")
        if album is not None:
            self.set_album(album.text)

    def __get_json(self):
        import requests
        import lastFmData

        temp = self.get_title()
        parameters_dict = {'api_key': lastFmData.API_KEY,
                           'artist': self.get_artist(), 'track': temp,
                           'method': 'track.getinfo', 'format': 'json'}
        try:
            response = requests.get('http://' + lastFmData.URL + '/2.0/', parameters_dict)
            return response.json()
        except requests.exceptions.RequestException as e:
            print('Error: ' + e.strerror)

    def __get_xml(self):
        import requests as rl
        import lastFmData

        parameters_dict = {'api_key': lastFmData.API_KEY,
                           'artist': self.get_artist(),
                           'track': self.get_title(),
                           'method': "track.getinfo"}
        try:
            response = rl.get('http://' + lastFmData.URL + '/2.0/', parameters_dict)
            return response.text
        except rl.exceptions.RequestException as e:
            print('Ошибка: ' + e.strerror)

    def __get_album_xml(self):
        import requests as rl
        import lastFmData

        parameters_dict = {'api_key': lastFmData.API_KEY,
                           'artist': self.get_artist(),
                           'album': self.get_album(),
                           'method': "album.getinfo"}
        try:
            response = rl.get('http://' + lastFmData.URL + '/2.0/', parameters_dict)
            return response.text
        except rl.exceptions.RequestException as e:
            print('Ошибка: ' + e.strerror)

    @staticmethod
    def __get_picture_url_from_xml(xml):
        from bs4 import BeautifulSoup
        result = BeautifulSoup(xml, "xml")
        if result.find('image', size='extralarge') is not None:
            return result.find('image', size='extralarge').text
        elif result.find('image', size='large') is not None:
            return result.find('image', size='large').text
        else:
            return ''

    @staticmethod
    def __get_picture_file(url):
        import urllib.request as url_request
        import urllib.error
        import os
        from PIL import Image
        if url == '':
            return ''
        temp_file = 'temp' + url[url.rfind('.'):]
        try:
            picture_bytes = url_request.urlopen(url).read()
        except urllib.error.URLError:
            return ''
        picture = open(temp_file, 'wb')
        picture.write(picture_bytes)
        picture.close()
        pic = Image.open(temp_file)
        pic.save('temp.jpg')
        os.unlink(temp_file)
        return 'temp.jpg'

    def __set_picture(self, file_name):
        import os
        if not os.path.exists(file_name):
            return
        with open(file_name, 'rb') as picture_file:
            picture_bytes = picture_file.read()
            self.set_picture(picture_bytes)
