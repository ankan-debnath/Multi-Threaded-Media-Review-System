import os
import  sqlite3
from rich.table import Table
from rich.console import Console
from dotenv import  load_dotenv

from enum import Enum
import db
from observer import  Observer

class MediaType(Enum):
    MOVIE = "movie"
    SONG = "song"
    WEB_SHOW = "web_show"

console = Console()
load_dotenv()

class ReviewSystem:
    def __init__(self):
        self.observer = Observer()

    def print_reviews(self, reviews, title):
        table = Table(title=f"Title : {title}", title_style="bold cyan")
        table.add_column("user_name", style="cyan", justify="center")
        table.add_column("Rating", style="magenta")
        table.add_column("Comment", style="magenta", justify="center")
        for user_name, rating, comment in reviews:
            table.add_row(user_name, str(rating), comment)
        console.print(table)

    def print_media(self, media_data):
        """Display media list with rich formatting."""
        table = Table(title="Media List")
        table.add_column("ID", style="cyan", justify="center")
        table.add_column("Type", style="magenta")
        table.add_column("Title", style="magenta", justify="center")
        for media_id, media_type, title, _ in media_data:
            table.add_row(str(media_id), media_type, title)

        console.print(table)

    def print_top_medias(self, medias, category):
        """Display media list with rich formatting."""
        table = Table(title=f"Top Rated {category} List", title_style="bold cyan")
        table.add_column("Name", style="cyan")
        table.add_column("Average Rating", style="magenta", justify="center")
        for media_name, rating in medias:
            table.add_row(media_name,str(rating))
        console.print(table)

    def print_recommendations(self, recommendations, user ,category=""):
        table = Table(title=f"Recommendations For {user} {('Category : ' + category) if category else ''}", title_style="bold cyan")
        table.add_column("ID", style="cyan")
        table.add_column("Name", style="magenta", justify="center")
        table.add_column("Category", style="magenta", justify="center")
        table.add_column("Average Rating", style="magenta", justify="center")
        table.add_column("Recommendation Type", style="magenta", justify="center")

        for media_id, media_name, media_type, avg_rating, recommendation_type in recommendations:
            table.add_row(str(media_id), media_name, media_type, str(avg_rating), recommendation_type)

        console.print(table)


    def list_media(self):
        try:
            with sqlite3.connect('media.db', check_same_thread=False) as conn:
                media_data = db.get_all_media(conn)

            self.print_media(media_data)

        except sqlite3.DatabaseError as err:
            console.print(f"[red]Error:[/red] Database error. Message : {err}")

    def submit_review(self, user_name, media_cred, rating, comment):
        """Submit a review with styled output."""
        try:
            media_id = int(media_cred) if media_cred.isdigit() else None
            media_name = media_cred if not media_cred.isdigit() else None
            rating = float(rating)

            with sqlite3.connect('media.db', check_same_thread=False) as conn:
                if not (1 <= rating <= 5):
                    console.print("[red]Error:[/red] Rating must be between 1 and 5.")
                    return

                if media_id:
                    db.add_review_with_media_id(user_name, media_id, rating, comment, conn)
                if media_name:
                    media_id = db.add_review_with_media_name(user_name, media_name, rating, comment, conn)

                self.observer.notify(media_id, rating, comment, conn)
        except ValueError:
            console.print("[red]Error:[/red] Media ID must integer and Rating must be decimal value.")
        except sqlite3.IntegrityError:
            console.print(f"[red]Error:[/red] media_id or user_name is invalid ", )
        except sqlite3.OperationalError as err:
            console.print(f"[red]Error:[/red] Database error : {err}")

    def create_user(self, user_name, password):
        if password != os.getenv("admin_password"):
            console.print("[red]Error:[/red] Wrong Password")
            return
        try:
            with sqlite3.connect('media.db', check_same_thread=False) as conn:
                db.create_user(user_name, conn)

        except sqlite3.OperationalError as e:
            console.print("[red]Error:[/red] DB Error", e)

    def add_media(self, user_name, media_type, media_name):
        try:
            with sqlite3.connect('media.db', check_same_thread=False) as conn:
                user_name, media_type, media_name = user_name, MediaType[media_type.upper()].value, media_name

                db.add_media(user_name, media_type, media_name, conn)

                console.print(f"[green]Media added \nType : {media_type}, \nName : {media_name}[/green]", style='cyan')
        except KeyError:
            console.print("[red]Error:[/red] Media Type must be movie, song or web_show")
        except sqlite3.OperationalError as err:
            console.print(f"[red]Error:[/red] Database error : {err}")

    def subscribe_to_media(self, user_name, media_id):
        try:
            with sqlite3.connect('media.db', check_same_thread=False) as conn:
                self.observer.subscribe(user_name, int(media_id), conn)

        except ValueError as err:
            console.print(f"[red]Error:[/red] Failed to subscribe, media_id must be integer \nMessage : {err}")
        except sqlite3.OperationalError as err:
            console.print(f"[red]Error:[/red] Failed to subscribe. Message : {err}")

    def search(self, title):
        try:
            with sqlite3.connect('media.db', check_same_thread=False) as conn:
                reviews = db.get_reviews_by_title(title, conn)
                self.print_reviews(reviews, title)
                # self.print_media(media_data)
                # console.print(f"[green]Media added \nType : {media_type}, \nName : {media_name}[/green]", style='cyan')
        except KeyError:
            console.print("[red]Error:[/red] Media Type must be movie, song or web_show")
        except sqlite3.OperationalError as err:
            console.print(f"[red]Error:[/red] Database error : {err}")

    def get_top_rated_media(self, category):
        try:
            with sqlite3.connect('media.db', check_same_thread=False) as conn:
                category = MediaType[category.upper()].value

                medias = db.get_top_rated_media(category, conn)
                self.print_top_medias(medias[:5], category)

        except KeyError:
            console.print("[red]Error:[/red] Category must be movie, song or web_show")
        except sqlite3.OperationalError as err:
            console.print(f"[red]Error:[/red] Database error : {err}")

    def get_recommendation_with_category(self, user_name, category=""):
        try:
            with sqlite3.connect('media.db', check_same_thread=False) as conn:
                media_type = MediaType[category.upper()].value if category else category

                recommendations = db.get_recommendations_from_review_data(user_name, media_type, conn)
                recommendations += db.get_recommendations_from_subscriber_data(user_name, media_type, conn)

                # Filtering the duplicate recommendations
                seen = set()
                final_recommendations = []
                for media in recommendations:
                    media_id = media[0]
                    if media_id not in seen:
                        final_recommendations.append(media)
                        seen.add(media_id)

                self.print_recommendations(final_recommendations, user_name, category)

        except KeyError:
            console.print("[red]Error:[/red] Media Type must be movie, song or web_show")
        except sqlite3.OperationalError as err:
            console.print(f"[red]Error:[/red] Database error : {err}")

    def get_recommendation(self, user_name):
        pass