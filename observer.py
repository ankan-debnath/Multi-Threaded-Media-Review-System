import sqlite3
from rich.console import  Console
from rich.panel import Panel

console = Console()

class Observer:

    def notify_subscriber(self, user_name, media_title, media_type, rating, comment):
        message = (
            f"[bold cyan]📢 New Review Alert![/bold cyan]\n"
            f"[green]Media:[/green] {media_title}\n"
            f"[green]Type:[/green] {media_type}\n"
            f"[yellow]Rating:[/yellow] ⭐ {rating}/5\n"
            f"[blue]Comment:[/blue] {comment}\n"
            f"[magenta]Hey {user_name}, check it out![/magenta]"
        )

        console.print(Panel(message, title="[bold red]Notification[/bold red]", expand=False))

    def subscribe(self, user_name, media_id, conn):
        conn.execute('PRAGMA foreign_keys = ON;')
        c = conn.cursor()
        c.execute(
            '''CREATE TABLE IF NOT EXISTS SUBSCRIBERS(
                media_id INTEGER,
                user_name TEXT,
                FOREIGN KEY (media_id) REFERENCES MEDIAS(media_id),
                FOREIGN KEY (user_name) REFERENCES USERS(user_name),
                PRIMARY KEY (media_id, user_name)
            )''')

        try:
            c.execute("INSERT INTO SUBSCRIBERS VALUES(?, ?)", (media_id, user_name))
            console.print(f"[green]{user_name} added as subscriber to media id : {media_id} ", style='cyan')

        except sqlite3.IntegrityError as err:
            console.print(f"[red]Error:[/red] media_id or user does not exist or user already subscribed: {err}", )

    def notify(self, media_id, rating, comment, conn):
        conn.execute('PRAGMA foreign_keys = ON;')
        c = conn.cursor()

        try:
            c.execute(
                '''CREATE TABLE IF NOT EXISTS SUBSCRIBERS(
                    media_id INTEGER,
                    user_name TEXT,
                    FOREIGN KEY (media_id) REFERENCES MEDIAS(media_id),
                    FOREIGN KEY (user_name) REFERENCES USERS(user_name),
                    PRIMARY KEY (media_id, user_name)
                )''')
            c.execute('''SELECT media_type, media_name FROM MEDIAS WHERE media_id = ?''', (media_id,))
            media = c.fetchall()
            media_type, media_name = media[0] if media else None, None
            c.execute('''SELECT user_name FROM SUBSCRIBERS WHERE media_id = ?''', (media_id,) )
            subscribers = c.fetchall()

            for subscriber in subscribers:
                self.notify_subscriber(subscriber[0], media_name, media_type, rating, comment)

        except sqlite3.IntegrityError as err:
            console.print(f"[red]Error:[/red] media_id or user does not exist : {err}", )
        except sqlite3.OperationalError as err:
            console.print(f"[red]Error:[/red] Database error : {err}", )

        conn.commit()
