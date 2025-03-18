import os
import  sqlite3
import threading
from threading import Thread
import redis
from rich.table import Table
from rich.console import Console
from dotenv import  load_dotenv
import  json
import asyncio

from enum import Enum
from src import db
from src.observer import  Observer
from src.redis_db import redis_client, is_redis_available

class MediaType(Enum):
    MOVIE = "movie"
    SONG = "song"
    WEB_SHOW = "web_show"

console = Console()
load_dotenv()

redis_available = is_redis_available(redis_client)

lock = threading.Lock()

CACHE_EXPIRY = 1800     # cache is invalidated automatically after 30 minutes

class ReviewSystem:
    def __init__(self):
        self.observer = Observer()
        try:
            with sqlite3.connect('media.db', check_same_thread=False) as conn:
                db.create_all_db_tables(conn)
        except sqlite3.DatabaseError as err:
            console.print(f"[red]Error:[/red] Database error. Message : {err}")

    def print_reviews(self, reviews, title):
        table = Table(title=f"Title : {title}", title_style="bold cyan")
        table.add_column("user_name", style="cyan", justify="center")
        table.add_column("Rating", style="magenta")
        table.add_column("Comment", style="magenta")
        for user_name, rating, comment in reviews:
            table.add_row(user_name, str(rating), comment)
        console.print(table)

    def print_media(self, media_data):
        """Display media list with rich formatting."""
        table = Table(title="Media List")
        table.add_column("ID", style="cyan", justify="center")
        table.add_column("Type", style="magenta")
        table.add_column("Title", style="magenta")
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
        table.add_column("Name", style="magenta")
        table.add_column("Category", style="magenta", justify="center")
        table.add_column("Average Rating", style="magenta", justify="center")
        table.add_column("Recommendation Type", style="magenta")

        for media_id, media_name, media_type, avg_rating, recommendation_type in recommendations:
            table.add_row(str(media_id), media_name, media_type, str(avg_rating), recommendation_type)

        console.print(table)


    def list_media(self):
        try:
            cache_key = "media_list"
            cached_data = None

            if redis_available:
                cached_data = redis_client.get(cache_key)

            if cached_data:
                print("Data from cache")
                media_data = json.loads(cached_data)
            else:
                print("Data from DB")
                with sqlite3.connect('media.db', check_same_thread=False) as conn:
                    media_data = db.get_all_media(conn)
                    if redis_available:
                        redis_client.setex(cache_key, CACHE_EXPIRY, json.dumps(media_data))         # caching the media_list

            self.print_media(media_data)

        except sqlite3.DatabaseError as err:
            console.print(f"[red]Error:[/red] Database error. Message : {err}")
        except redis.ConnectionError as err:
            console.print(f"[red]Error:[/red] Redis Cache error. Message : {err}")

    def submit_review(self, user_name, media_cred, rating, comment):
        """Submit a review with styled output."""
        try:
            media_id = int(media_cred) if media_cred.isdigit() else None
            media_name = media_cred.lower() if not media_cred.isdigit() else None
            rating = float(rating)

            with lock:
                with sqlite3.connect('media.db') as conn:
                    if not (1 <= rating <= 5):
                        console.print("[red]Error:[/red] Rating must be between 1 and 5.")
                        return

                    if media_id:
                        db.add_review_with_media_id(user_name, media_id, rating, comment, conn)
                    if media_name:
                        media_id = db.add_review_with_media_name(user_name, media_name, rating, comment, conn)

                    media_type = db.get_media_type(media_id, conn)

                # cache invalidation operations
                if media_id and redis_available and redis_client.get(media_id):
                    redis_client.delete(media_id)
                if media_name and redis_available and redis_client.get(media_name):
                    redis_client.delete(media_name)

                if redis_available and redis_client.get(f"top_rated_{media_type}"):
                    redis_client.delete(f"top_rated_{media_type}")

            asyncio.run(self.observer.notify(media_id, rating, comment, conn))  # send notification to users asynchronously

        except ValueError:
            console.print("[red]Error:[/red] Media ID must integer and Rating must be decimal value.")
        except sqlite3.IntegrityError:
            console.print(f"[red]Error:[/red] media_id or user_name is invalid ", )
        except sqlite3.OperationalError as err:
            console.print(f"[red]Error:[/red] Database error : {err}")
        except redis.exceptions.RedisError as err:
            console.print(f"[red]Error:[/red] Redis Cache error. Message : {err}")

    def create_user(self, user_name, password):
        if password != os.getenv("admin_password"):
            console.print("[red]Error:[/red] Wrong Password")
            return
        try:
            with sqlite3.connect('media.db', check_same_thread=False) as conn:
                db.create_user(user_name, conn)

        except sqlite3.OperationalError as e:
            console.print("[red]Error:[/red] DB Error", e)

    def add_media(self, media):
        try:
            user_name, media_type, media_name = media.get_user_name(), media.get_media_type(), media.get_name()
            with sqlite3.connect('media.db', check_same_thread=False) as conn:
                user_name, media_type, media_name = user_name, media_type, media_name

                db.add_media(user_name, media_type, media_name, conn)
                if redis_available:
                    redis_client.delete("media_list")                       #invalidating the cache

            console.print(f"[green]Media added \nType : {media_type}, \nName : {media_name}[/green]", style='cyan')

        except (KeyError, AttributeError):
            console.print("[red]Error:[/red] Media Type must be movie, song or web_show")
        except sqlite3.OperationalError as err:
            console.print(f"[red]Error:[/red] Database error : {err}")
        except sqlite3.IntegrityError as err:
            console.print(f"[red]Error:[/red] User is invalid or Media already exists : {err}")
        except redis.ConnectionError as err:
            console.print(f"[red]Error:[/red] Redis Cache error. Message : {err}")

    def subscribe_to_media(self, user_name, media_cred):
        try:
            with sqlite3.connect('media.db', check_same_thread=False) as conn:
                media_id = db.is_media_available(media_cred, conn)

                if not db.is_available(user_name, conn):
                    raise sqlite3.IntegrityError("user_name does not exist!")
                if not media_id:
                    raise sqlite3.IntegrityError("media not available!")
                if db.is_subscribed(user_name, media_id, conn):
                    raise sqlite3.IntegrityError("user already subscribed!")

                self.observer.subscribe(user_name, int(media_id), conn)

        except ValueError as err:
            console.print(f"[red]Error:[/red] Failed to subscribe, media_id must be integer \nMessage : {err}")
        except sqlite3.IntegrityError as err:
            console.print(f"[red]Error:[/red] Failed to subscribe. Message : {err}", )
        except sqlite3.OperationalError as err:
            console.print(f"[red]Error:[/red] Failed to subscribe. Message : {err}")

    def search(self, title):
        try:
            cache_key = title.lower()
            cached_data = None

            if redis_available:
                cached_data = redis_client.get(cache_key)

            if cached_data:
                reviews = json.loads(cached_data)
                print("Reviews from cache")

            else:
                with sqlite3.connect('media.db', check_same_thread=False) as conn:
                    print("Reviews from DB")
                    reviews = db.get_reviews_by_title(title, conn)
                    if redis_available:
                        redis_client.setex(cache_key, CACHE_EXPIRY, json.dumps(reviews))

            self.print_reviews(reviews, title)

        except KeyError:
            console.print("[red]Error:[/red] Media Type must be movie, song or web_show")
        except sqlite3.OperationalError as err:
            console.print(f"[red]Error:[/red] Database error : {err}")
        except redis.ConnectionError as err:
            console.print(f"[red]Error:[/red] Redis Cache error. Message : {err}")

    def get_top_rated_media(self, category):
        try:
            category = MediaType[category.upper()].value
            cached_data = None

            cache_key = f"top_rated_{category}"
            if redis_available:
                cached_data = redis_client.get(cache_key)

            if cached_data:
                medias = json.loads(cached_data)
                print("Top rated media from cache")
            else:
                with sqlite3.connect('media.db', check_same_thread=False) as conn:
                    medias = db.get_top_rated_media(category, conn)
                    if redis_available:
                        redis_client.setex(cache_key, CACHE_EXPIRY, json.dumps(medias))
                    print("Top rated media from DB")

            self.print_top_medias(medias, category)

        except KeyError:
            console.print("[red]Error:[/red] Category must be movie, song or web_show")
        except sqlite3.OperationalError as err:
            console.print(f"[red]Error:[/red] Database error : {err}")
        except redis.ConnectionError as err:
            console.print(f"[red]Error:[/red] Redis Cache error. Message : {err}")

    def get_recommendation_with_category(self, user_name, category=""):
        try:
            with sqlite3.connect('media.db', check_same_thread=False) as conn:
                media_type = MediaType[category.upper()].value if category else category

                if not db.is_available(user_name, conn):
                    raise sqlite3.IntegrityError("user_name does not exist!")

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
        except sqlite3.IntegrityError as err:
            console.print(f"[red]Error:[/red] recommendation error : {err}")

    def submit_multiple_reviews(self, reviews):
        try:
            reviews = reviews.replace(" ", "")
            reviews = reviews.strip("[]()")
            reviews = reviews.split("),(")

            final_reviews = []

            for item in reviews:
                user_name, media_cred, rating, comment = item.split(",")
                user_name = user_name.strip("'")
                media_cred = media_cred.strip("'")
                rating = rating.strip("'")
                comment = comment.strip("'")
                final_reviews.append(tuple([user_name, media_cred, rating, comment]))

            # print(final_reviews)

            review_threads = []

            for review in final_reviews:
                user_name, media_cred, rating, comment = review
                thread = Thread(target=self.submit_review, args=(user_name, media_cred, rating, comment))
                review_threads.append(thread)
                thread.start()

            for thread in review_threads:
                thread.join()

        except KeyError:
            console.print("[red]Error:[/red] Media Type must be movie, song or web_show")
        except InterruptedError as err:
            console.print(f"[red]Error:[/red] Execution error : {err}")
