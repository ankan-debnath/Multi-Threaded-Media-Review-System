from abc import  ABC, abstractmethod

class Media(ABC):
    @abstractmethod
    def get_media_type(self):
        pass
    def get_name(self):
        pass
    # def __str__(self):
    #     return f"{self.get_media_type()}, {self.get_name()}"

class Movie(Media):
    def __init__(self, name):
        self.name = name

    def get_media_type(self):
        return "movie"

    def get_name(self):
        return self.name

class WebShow(Media):
    def __init__(self, name):
        self.name = name

    def get_media_type(self):
        return "web show"

    def get_name(self):
        return self.name

class Song(Media):
    def __init__(self, name):
        self.name = name

    def get_media_type(self):
        return "song"

    def get_name(self):
        return self.name

class MediaFactory:
    @staticmethod
    def create_media(media_type, name):
        medias = { "movie" : Movie, "song" : Song, "web show" : WebShow }
        return medias[media_type.lower()](name) if media_type.lower() in medias else None