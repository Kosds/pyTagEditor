def putFromName(path):
    import os, re
    from mutagen.mp3 import EasyMP3 as mp3
    if path[-1] != '/':
        path += '/'
    try:        
        files = filter(lambda x: x.endswith('.mp3'), os.listdir(path))
    except OSError:
        print('Error of path')
    else:
        for name in files:    
            track = mp3(path + name)
            try:
                artist, title = name[0:-4].split(' - ')
            except ValueError:
                continue
            else:
                track['title'] = title
                track['artist'] = artist
                track.save()                
        print('Завершено')

def clearAlbums(path):
    import os
    from mutagen.mp3 import MP3 as mp3    
    if path[-1] != '/':
        path += '/'
    try:        
        files=filter(lambda x: x.endswith('.mp3'),os.listdir(path))
    except OSError:
        print('Error of path')
    else:
        finded=False
        for name in files:
            track=mp3(path+name)
            if 'TALB' in list(track.keys()) and len(track['TALB'].text[0])>0 and '.' in track['TALB'].text[0]:
                print(track['TALB'].text[0]+' | y/n')
                finded=True
                if input()=='y':
                    track['TALB'].text[0]=' '
                    track.save()
                else: continue
        if ~finded: print('Не найдены')
        print('Завершено')

class trackTags(object):
    def __init__(self, trackPath):
        from mutagen.mp3 import MP3 as mp3
        try:
            self.__track = mp3(trackPath)
        except FileNotFoundError:
            print('Error path')

    def getAlbumTitle(self):
        import re
        for item in list(self.__track.keys()):
            if re.match('TAL', item):
                return self.__track[item].text[0]
        raise RuntimeError('Альбом не задан')
    
    def getAlbumPicture(self):
        import re
        for item in list(self.__track.keys()):
            if re.match('APIC',item):
                return self.__track[item].data
        raise RuntimeError('Обложка не задана')

    def getArtist(self):
        import re
        for item in list(self.__track.keys()):
            if re.match('TPE', item):
                return self.__track[item].text[0]
        raise RuntimeError('Исполнитель не задан')

    def getTitle(self):
        import re
        for item in list(self.__track.keys()):
            if re.match('TIT', item):
                return self.__track[item].text[0]
        raise RuntimeError('Название не задано')

    def setAlbumTitle(self,albumTitle):
        from mutagen import id3
        self.__track['TALB'] = id3.TALB(encoding = 3, text = albumTitle)
        self.__track.save()
        del id3

    def setAlbumPicture(self,pictureStr):
        from mutagen import id3
        import re

        flag = False
        for item in list(self.__track.keys()):
            if re.match('APIC', item):
                self.__track.tags.pop(item)
        self.__track.tags['APIC:'] = id3.APIC(encoding=3, mime='image/jpeg', type=3, data=pictureStr)
        self.__track.save(v1=2)
        del id3

    def setArtist(self,artistName):
        from mutagen import id3
        self.__track['TPE1'] = id3.TPE1(encoding=3, text=artistName)
        self.__track.save()
        del id3

    def setTitle(self,trackTitle):
        from mutagen import id3
        self.__track['TIT1'] = id3.TIT1(encoding = 3, text = trackTitle)
        self.__track.save()
        del id3

    def setAlbumPictureLastFm(self):
        xml = self.__getXML()
        pictureUrl = self.__getPictureUrlFromXml(xml)
        pictureName = self.__getPictureFile(pictureUrl)
        self.__setPicture(pictureName)

    def __getJSON(self):
        import requests as rl

        API_KEY = '70578b40668e460c6282ee394e448586'
        URL = 'ws.audioscrobbler.com'
        temp = self.getTitle()
        parametersDict=dict(api_key = API_KEY, artist = self.getArtist(), track = temp, method = 'track.getinfo',format = 'json')
        try:
            response = rl.get('http://'+URL+'/2.0/',parametersDict)
        except rl.exceptions.RequestException as e:
            print('Ошибка: ' + e.strerror)
        else:
            return response.json()

    def __getXML(self):
        import requests as rl
        API_KEY = '70578b40668e460c6282ee394e448586'
        URL = 'ws.audioscrobbler.com'
        parametersDict = dict(api_key=API_KEY, artist=self.getArtist(), track=self.getTitle(), method='track.getinfo')
        try:
            response = rl.get('http://' + URL + '/2.0/', parametersDict)
        except rl.exceptions.RequestException as e:
            print('Ошибка: ' + e.strerror)
        else:
            return response.text

    def __getPictureUrlFromXml(self,xml):
        from bs4 import BeautifulSoup as bs
        result = bs(xml, 'xml')
        if result.find('image',size='extralarge') != None:
            return result.find('image',size='extralarge').text
        elif result.find('image',size='large') != None:
            return result.find('image',size='large').text
        else:
            return ''

    def __getPictureFile(self, url):
        import urllib as ul
        from PIL import Image

        if url == '':
            return 'gag.jpg'

        temp = 'temp'+url[url.rfind('.'):]
        pictureFile = open(temp,'wb')
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

    def __setPicture(self,fileName):
        if fileName == '':
            return
        try:
            pictureFile = open(fileName,'rb')
            pictureStr = pictureFile.read()
        except OSError('Неверное имя файла') as e:
            print(e.strerror)
        else:
             self.setAlbumPicture(pictureStr)
        finally:
            pictureFile.close()