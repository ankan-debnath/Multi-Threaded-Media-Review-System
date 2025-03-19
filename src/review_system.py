import os
import  sqlite3
import threading
from concurrent.futures.thread import ThreadPoolExecutor
from threading import Thread
import redis
from rich.console import Console
from dotenv import  load_dotenv
import  json
import asyncio

from enum import Enum
from src import db
from src.Observer import  Observer
from src.redis_db import get_redis_client, is_redis_available
from src.printer import Printer
from src.User import User

class MediaType(Enum):
    MOVIE = "movie"
    SONG = "song"
    WEB_SHOW = "web_show"

console = Console()
load_dotenv()


lock = threading.Lock()

CACHE_EXPIRY = 1800     # cache is invalidated automatically after 30 minutes

class ReviewSystem:
    def __init__(self, test_file):
        self.printer = Printer()
        self.db_file = test_file
        self.redis_client = get_redis_client()
        self.redis_available = is_redis_available(self.redis_client)


        try:
            with sqlite3.connect(self.db_file, check_same_thread=False) as conn:
                db.create_all_db_tables(conn, lock)
        except sqlite3.DatabaseError as err:
            console.print(f"[red]Error:[/red] Database error. Message : {err}")

    def list_media(self):
        try:
            cache_key = "media_list"
            cached_data = None

            if self.redis_available:
                cached_data = self.redis_client.get(cache_key)

            if cached_data:
                print("Data from cache")
                media_data = json.loads(cached_data)
            else:
                print("Data from DB")
                with sqlite3.connect(self.db_file, check_same_thread=False) as conn:
                    media_data = db.get_all_media(conn, lock)
                    if self.redis_available:
                        self.redis_client.setex(cache_key, CACHE_EXPIRY, json.dumps(media_data))         # caching the media_list

            return media_data

        except sqlite3.DatabaseError as err:
            return f"[red]Error:[/red] Database error. Message : {err}"
        except redis.ConnectionError as err:
            return f"[red]Error:[/red] Redis Cache error. Message : {err}"

    def submit_review(self, user_name, media_cred, rating, comment):
        """Submit a review with styled output."""
        try:
            rating = float(rating)
            if not (1 <= rating <= 5):
                raise ValueError("Rating must be between 1 and 5.")

            with sqlite3.connect(self.db_file) as conn:

                media_id = db.is_media_available(media_cred, conn, lock)

                if not db.is_available(user_name, conn, lock):
                    raise sqlite3.IntegrityError("user_name not found")
                if not media_id:
                    raise sqlite3.IntegrityError("media not found")

                media = db.get_medias(media_id, conn, lock)
                media_type, media_name = media[0]
                media_name = media_name.lower()

                subscribers = db.get_all_subscribers(media_id, conn, lock)
                observers = [ Observer(cur_user) for cur_user,  in subscribers if cur_user != user_name]

                user = User(user_name, observers)
                user.add_review(media_id, rating, comment, conn, lock)

                # cache invalidation operations
                if self.redis_available and self.redis_client.get(media_id):
                    self.redis_client.delete(media_id)
                if self.redis_available and self.redis_client.get(media_name):
                    self.redis_client.delete(media_name)

                if self.redis_available and self.redis_client.get(f"top_rated_{media_type}"):
                    self.redis_client.delete(f"top_rated_{media_type}")

            # send notification to users asynchronously
            asyncio.run(user.notify_observers(media_name, media_type, rating, comment))
            return f"[green]Review added by \nUser : {user_name}\nMedia : {media_cred}, Rating : {rating},\nComment : {comment}[/green]"

        except ValueError as err:
            return f"[red]Error:[/red] : {err}"
        except sqlite3.IntegrityError as err:
            return f"[red]Error:[/red] message : {err}"
        except sqlite3.OperationalError as err:
            return f"[red]Error:[/red] Database error : {err}"
        except redis.exceptions.RedisError as err:
            return f"[red]Error:[/red] Redis Cache error. Message : {err}"

    def create_user(self, user_name, password):
        if password != os.getenv("admin_password"):
            return "[red]Error:[/red] Wrong Password"
        try:
            with sqlite3.connect(self.db_file, check_same_thread=False) as conn:
                db.create_user(user_name, conn, lock)
            return f"[green]User created with user_name : {user_name}[/green]"

        except sqlite3.IntegrityError:
            return f"[red]Error:[/red] Same user_name already exists : {user_name}"
        except sqlite3.OperationalError as e:
            return f"[red]Error:[/red] DB Error :  {e}"

    def add_media(self, media):
        try:
            user_name, media_type, media_name = media.get_user_name(), media.get_media_type(), media.get_name()
            with sqlite3.connect(self.db_file, check_same_thread=False) as conn:
                if not db.is_available(user_name, conn, lock):
                    raise sqlite3.IntegrityError("User does not exist")
                if db.is_media_available(media_name, conn, lock):
                    raise sqlite3.IntegrityError("Media already exists")


                db.add_media(user_name, media_type, media_name, conn, lock)

                if self.redis_available:
                    self.redis_client.delete("media_list")                       #invalidating the cache

            return f"[green]Media added \nType : {media_type}, \nName : {media_name}[/green]"

        except (KeyError, AttributeError):
            return "[red]Error:[/red] Media Type must be movie, song or web_show"
        except sqlite3.OperationalError as err:
            return f"[red]Error:[/red] Database error : {err}"
        except sqlite3.IntegrityError as err:
            return f"[red]Error:[/red] Add Media error, message : {err}"
        except redis.ConnectionError as err:
            return f"[red]Error:[/red] Redis Cache error. Message : {err}"

    def subscribe_to_media(self, user_name, media_cred):
        try:
            with sqlite3.connect(self.db_file, check_same_thread=False) as conn:
                media_id = db.is_media_available(media_cred, conn, lock)

                if not media_id:
                    raise sqlite3.IntegrityError("media not available!")
                if not db.is_available(user_name, conn, lock):
                    raise sqlite3.IntegrityError("user_name does not exist!")
                if db.is_subscribed(user_name, media_id, conn, lock):
                    raise sqlite3.IntegrityError("user already subscribed!")

                user = User(user_name)
                user.subscribe(media_id, conn, lock)
                return f"[green]User : {user_name}, added as a subscriber to media : {media_cred}[/green]"

        except ValueError as err:
            return f"[red]Error:[/red] Failed to subscribe, media_id must be integer \nMessage : {err}"
        except sqlite3.IntegrityError as err:
            return f"[red]Error:[/red] Failed to subscribe. Message : {err}"
        except sqlite3.OperationalError as err:
            return f"[red]Error:[/red] Failed to subscribe. Message : {err}"

    def unsubscribe_to_media(self, user_name, media_cred):
        try:
            with sqlite3.connect(self.db_file, check_same_thread=False) as conn:
                media_id = db.is_media_available(media_cred, conn, lock)

                if not media_id:
                    raise sqlite3.IntegrityError("media not available!")
                if not db.is_available(user_name, conn, lock):
                    raise sqlite3.IntegrityError("user_name does not exist!")
                if not db.is_subscribed(user_name, media_id, conn, lock):
                    raise sqlite3.IntegrityError(f"{user_name} is not subscribed to {media_cred}")

                user = User(user_name)
                user.unsubscribe(media_id, conn, lock)
                return f"[green]User : {user_name}, unsubscribed from media : {media_cred}[/green]"


        except ValueError as err:
            return f"[red]Error:[/red] Failed to unsubscribe, media_id must be integer \nMessage : {err}"
        except sqlite3.IntegrityError as err:
            return f"[red]Error:[/red] Failed to unsubscribe. Message : {err}"
        except sqlite3.OperationalError as err:
            return f"[red]Error:[/red] Failed to unsubscribe. Message : {err}"


    def search(self, title):
        try:
            cache_key = title.lower()
            cached_data = None
            reviews = []

            if self.redis_available:
                cached_data = self.redis_client.get(cache_key)

            if cached_data:
                reviews = json.loads(cached_data)
                print("Reviews from cache")

            else:
                with sqlite3.connect(self.db_file, check_same_thread=False) as conn:
                    print("Reviews from DB")
                    media_id = db.is_media_available(title, conn, lock)
                    if not media_id:
                        raise sqlite3.IntegrityError("Media not found")

                    reviews = db.get_reviews_by_title(title, conn, lock)
                    if self.redis_available:
                        self.redis_client.setex(cache_key, CACHE_EXPIRY, json.dumps(reviews))

            return reviews, title

        except KeyError:
            return f"[red]Error:[/red] Media Type must be movie, song or web_show"
        except sqlite3.IntegrityError as err:
            return f"[red]Error:[/red] Search Error, message : {err}"
        except sqlite3.OperationalError as err:
            return f"[red]Error:[/red] Database error : {err}"
        except redis.ConnectionError as err:
            return f"[red]Error:[/red] Redis Cache error. Message : {err}"

    def get_top_rated_media(self, category):
        try:
            category = MediaType[category.upper()].value
            cached_data = None

            cache_key = f"top_rated_{category}"
            if self.redis_available:
                cached_data = self.redis_client.get(cache_key)

            if cached_data:
                medias = json.loads(cached_data)
                print("Top rated media from cache")
            else:
                with sqlite3.connect(self.db_file, check_same_thread=False) as conn:
                    medias = db.get_top_rated_media(category, conn, lock)
                    if self.redis_available:
                        self.redis_client.setex(cache_key, CACHE_EXPIRY, json.dumps(medias))
                    print("Top rated media from DB")

            return medias, category
        except KeyError:
            return "[red]Error:[/red] Category must be movie, song or web_show"
        except sqlite3.OperationalError as err:
            return f"[red]Error:[/red] Database error : {err}"
        except redis.ConnectionError as err:
            return f"[red]Error:[/red] Redis Cache error. Message : {err}"

    def get_recommendation_with_category(self, user_name, category=""):
        try:
            with sqlite3.connect(self.db_file, check_same_thread=False) as conn:
                media_type = MediaType[category.upper()].value if category else category

                if not db.is_available(user_name, conn, lock):
                    raise sqlite3.IntegrityError("user_name does not exist!")

                # recommendation based on review
                recommendations = db.get_recommendations_from_review_data(user_name, media_type, conn, lock)
                # recommendations based on subscription data
                recommendations += db.get_recommendations_from_subscriber_data(user_name, media_type, conn, lock)

                # Filtering the duplicate recommendations
                seen = set()
                final_recommendations = []
                for media in recommendations:
                    media_id = media[0]
                    if media_id not in seen:
                        final_recommendations.append(media)
                        seen.add(media_id)

                # recommending top rated medias if data not available
                if not final_recommendations:
                    for c in ((category,) if category else ("movie", "song", "web_show")):
                        final_recommendations += db.get_top_rated_media(c, conn, lock)

                    final_recommendations = [(*r, "top rated") for r in final_recommendations ]
                return final_recommendations, user_name, category

        except KeyError:
            return "[red]Error:[/red] Media Type must be movie, song or web_show"
        except sqlite3.OperationalError as err:
            return f"[red]Error:[/red] Database error : {err}"
        except sqlite3.IntegrityError as err:
            return f"[red]Error:[/red] recommendation error : {err}"

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

            # review_threads = []

            user_names = [review[0] for review in final_reviews]
            media_creds = [review[1] for review in final_reviews]
            ratings = [review[2] for review in final_reviews]
            comments = [review[3] for review in final_reviews]

            with ThreadPoolExecutor() as executor:
                result = list(executor.map(self.submit_review, user_names, media_creds, ratings, comments))

            return result

            # for review in final_reviews:
            #     user_name, media_cred, rating, comment = review
            #     thread = Thread(target=self.submit_review, args=(user_name, media_cred, rating, comment))
            #     review_threads.append(thread)
            #     thread.start()

            # for thread in review_threads:
            #     thread.join()

        except ValueError:
            return f"[red]Error:[/red] Message : Problem in reviews syntax"
        except KeyError:
            console.print("[red]Error:[/red] Media Type must be movie, song or web_show")
        except InterruptedError as err:
            console.print(f"[red]Error:[/red] Execution error : {err}")