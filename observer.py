import sqlite3

from rich.console import  Console
import asyncio
import logging

import db

logging.basicConfig(
    filename="notifications.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)

console = Console()

class Observer:

    async def notify_subscriber(self, user_name, media_title, media_type, rating, comment):
        message = (
            f" New Review Alert!\n"
            f"Media: {media_title}\n"
            f"Type: {media_type}\n"
            f"Rating:  {rating}/5\n"
            f"Comment: {comment}\n"
            f"Hey {user_name}, check it out!\n"
        )

        # await asyncio.sleep(10)     # simulating the delay for notifications
        logging.info(message)

    def subscribe(self, user_name, media_id, conn):
        db.subscribe_to_media(user_name, media_id, conn)
        console.print(f"[green]{user_name} added as subscriber to media id : {media_id} ", style='cyan')

    async def notify(self, media_id, rating, comment, conn):
        conn.execute('PRAGMA foreign_keys = ON;')
        c = conn.cursor()

        try:
            media = db.get_medias(media_id, conn)
            media_type, media_name = media[0] if media else (None, None)
            subscribers = db.get_all_subscribers(media_id, conn)

            for subscriber in subscribers:
                async with asyncio.TaskGroup() as tg:
                    tg.create_task(self.notify_subscriber(subscriber[0], media_name, media_type, rating, comment))

        except sqlite3.IntegrityError as err:
            console.print(f"[red]Error:[/red] media_id or user does not exist : {err}", )
        except sqlite3.OperationalError as err:
            console.print(f"[red]Error:[/red] Database error : {err}", )
        except InterruptedError as err:
            logging.ERROR("Notification error")

        conn.commit()
