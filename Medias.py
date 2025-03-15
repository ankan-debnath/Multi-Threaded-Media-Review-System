from abc import  ABC, abstractmethod

class Media(ABC):
    @abstractmethod
    def get_media_type(self):
        pass
    def get_name(self):
        pass

class Movie(Media):
    def __init__(self, user_name, name):
        self.name = name
        self.user_name = name

    def get_user_name(self):
        return self.user_name

    def get_media_type(self):
        return "movie"

    def get_name(self):
        return self.name

class WebShow(Media):
    def __init__(self, user_name, name):
        self.name = name
        self.user_name = name

    def get_user_name(self):
        return self.user_name

    def get_media_type(self):
        return "web_show"

    def get_name(self):
        return self.name

class Song(Media):
    def __init__(self, user_name, name):
        self.name = name
        self.user_name = name

    def get_user_name(self):
        return self.user_name

    def get_media_type(self):
        return "song"

    def get_name(self):
        return self.name

class MediaFactory:
    @staticmethod
    def create_media(user_name, media_type, name):
        medias = { "movie" : Movie, "song" : Song, "web_show" : WebShow }
        return medias[media_type](user_name, name)

    @staticmethod
    def save_media(media):
        media.save()