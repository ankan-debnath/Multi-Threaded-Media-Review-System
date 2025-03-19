import argparse

from src.medias import MediaFactory
from src.printer import Printer
from src.review_system import ReviewSystem

review_system = ReviewSystem()
printer = Printer()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Media Review System CLI")

    parser.add_argument("--list", action="store_true", help="List all media")
    parser.add_argument("--review", nargs=4, metavar=("USER_NAME", "MEDIA_ID/MEDIA_NAME", "RATING", "COMMENT"),
                        help="Submit a review")
    parser.add_argument("--add-media", nargs=3, metavar=("USER_NAME", "MEDIA_TYPE", "MEDIA_NAME"),
                        type=str, help="Add new Media")
    parser.add_argument("--search", nargs=1, metavar=("TITLE",), help="Search by title")
    parser.add_argument("--top-rated", nargs=1, metavar=("CATEGORY",),  help="Search top-rated movies with category")
    parser.add_argument("--recommend", nargs="+", metavar=("USER_ID", "CATEGORY"), help="Recommend media")
    parser.add_argument("--subscribe", nargs=2, metavar=("USER_NAME", "MEDIA_ID",), help="Subscribe to particular media")
    parser.add_argument("--unsubscribe", nargs=2, metavar=("USER_NAME", "MEDIA_ID",), help="Unsubscribe to particular media")
    parser.add_argument("--user", nargs=2, metavar=("USER_NAME", "ADMIN_PASSWORD",), help="Create User")

    parser.add_argument("--multiple-review", nargs=1, metavar=("REVIEWS",),
                        help="Submit a multiple reviews in format [ (USER_NAME, MEDIA_ID/MEDIA_NAME, RATING, COMMENT), ]\n Do not add any quotations in list")

    args = parser.parse_args()

    if args.list:
        media_list = review_system.list_media()
        if isinstance(media_list, list):
            printer.print_media(media_list)
        else:
            printer.print_message(media_list)

    elif args.user:
        user_name, password = args.user
        message = review_system.create_user(user_name, password)
        printer.print_message(message)

    elif args.top_rated:
        category = args.top_rated[0]
        medias = review_system.get_top_rated_media(category)
        if isinstance(medias, str):
            printer.print_message(medias)
        else:
            printer.print_top_medias(*medias)

    elif args.subscribe:
        user_name, media_id = args.subscribe
        message = review_system.subscribe_to_media(user_name, media_id)
        printer.print_message(message)


    elif args.unsubscribe:
        user_name, media_id = args.unsubscribe
        message = review_system.unsubscribe_to_media(user_name, media_id)
        printer.print_message(message)

    elif args.add_media:
        media = MediaFactory.create_media(*args.add_media)
        message = review_system.add_media(media)
        printer.print_message(message)

    elif args.review:
            user_name, media_cred, rating, comment = args.review
            review_system.submit_review(user_name, media_cred, rating, comment)
    elif args.multiple_review:
        reviews, = args.multiple_review
        review_system.submit_multiple_reviews(reviews)

    elif args.search:
        title = args.search[0]
        reviews = review_system.search(title)
        if isinstance(reviews, str):
            printer.print_message(reviews)
        else:
            printer.print_reviews(*reviews)

    elif args.recommend:
        user_name, category = args.recommend[0], args.recommend[1] if len(args.recommend) == 2 else None
        recommendations = review_system.get_recommendation_with_category(user_name, category if category else "")
        if isinstance(recommendations, str):
            printer.print_message(recommendations)
        else:
            printer.print_recommendations(*recommendations)

    else:
        parser.print_help()
