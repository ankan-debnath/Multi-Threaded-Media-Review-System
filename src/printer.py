from rich.table import Table
from rich.console import Console

class Printer:
    def __init__(self):
        self.console = Console()
    def print_reviews(self, reviews, title):
        table = Table(title=f"Title : {title}", title_style="bold cyan")
        table.add_column("user_name", style="cyan", justify="center")
        table.add_column("Rating", style="magenta")
        table.add_column("Comment", style="magenta")
        for user_name, rating, comment in reviews:
            table.add_row(user_name, str(rating), comment)
        self.console.print(table)

    def print_media(self, media_data):
        """Display media list with rich formatting."""
        table = Table(title="Media List")
        table.add_column("ID", style="cyan", justify="center")
        table.add_column("Type", style="magenta")
        table.add_column("Title", style="magenta")
        for media_id, media_type, title, _ in media_data:
            table.add_row(str(media_id), media_type, title)

        self.console.print(table)

    def print_top_medias(self, medias, category):
        """Display media list with rich formatting."""
        table = Table(title=f"Top Rated {category} List", title_style="bold cyan")
        table.add_column("ID", style="cyan")
        table.add_column("Name", style="cyan")
        table.add_column("Media Type", style="magenta", justify="center")
        table.add_column("Average Rating", style="magenta", justify="center")
        for media_id, media_name, media_type, rating in medias:
            table.add_row( str(media_id), media_name, media_type,str(rating))
        self.console.print(table)

    def print_recommendations(self, recommendations, user ,category=""):
        table = Table(title=f"Recommendations For {user} {('Category : ' + category) if category else ''}", title_style="bold cyan")
        table.add_column("ID", style="cyan")
        table.add_column("Name", style="magenta")
        table.add_column("Category", style="magenta", justify="center")
        table.add_column("Average Rating", style="magenta", justify="center")
        table.add_column("Recommendation Type", style="magenta")

        for media_id, media_name, media_type, avg_rating, recommendation_type in recommendations:
            table.add_row(str(media_id), media_name, media_type, str(avg_rating), recommendation_type)

        self.console.print(table)

    def print_message(self, message):
        self.console.print(message, style='cyan')