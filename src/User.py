import asyncio

from src import db

class User:
    def __init__(self, user_name, observer_list=[]):
        self.observer_list = observer_list
        self.user_name = user_name

    def subscribe(self, media_id, conn):
        db.subscribe_to_media(self.user_name, media_id, conn)

    def unsubscribe(self, media_id, conn, lock):
        db.unsubscribe(self.user_name, media_id, conn, lock)


    async def notify_observers(self, media_name, media_type, rating, comment):
        async with asyncio.TaskGroup() as tg:
            for observer in self.observer_list:
                tg.create_task(observer.update(media_name, media_type, rating, comment))

    def add_review(self, media_id, rating, comment, conn):
        db.add_review_with_media_id(self.user_name, media_id, rating, comment, conn)
