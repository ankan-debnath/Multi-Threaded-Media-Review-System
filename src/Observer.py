import sqlite3
from rich.console import  Console
import asyncio
import logging

from src import db

logging.basicConfig(
    filename="notifications.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)

console = Console()

class Observer:
    def __init__(self, user_name):
        self.user_name = user_name

    async def update(self, media_title, media_type, rating, comment):
        message = (
            f"Hey {self.user_name}, check it out!\n"
            f" New Review Alert!\n"
            f"Media: {media_title}\n"
            f"Type: {media_type}\n"
            f"Rating:  {rating}/5\n"
            f"Comment: {comment}\n"
        )

        # await asyncio.sleep(10)     # simulating the delay for notifications
        logging.info(message)
