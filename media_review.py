import argparse
from review_system import ReviewSystem


review_system = ReviewSystem()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Media Review System CLI")

    parser.add_argument("--list", action="store_true", help="List all media")
    parser.add_argument("--review", nargs=4, metavar=("USER_NAME", "MEDIA_ID", "RATING", "COMMENT"),
                        type=lambda x: int(x) if x.isdigit() else x, help="Submit a review")
    parser.add_argument("--add-media", nargs=3, metavar=("USER_NAME", "MEDIA_TYPE", "MEDIA_NAME"),
                        type=str, help="Add new Media")
    parser.add_argument("--search", nargs=1, metavar=("TITLE",), help="Search by title")
    parser.add_argument("--top-rated", nargs=1, metavar=("CATEGORY",),  help="Search top-rated movies with category")
    parser.add_argument("--recommend", nargs=1, metavar=("USER_ID",), help="Recommend media")
    parser.add_argument("--subscribe", nargs=2, metavar=("USER_NAME", "MEDIA_ID",), help="Subscribe to particular media")
    parser.add_argument("--user", nargs=2, metavar=("USER_NAME", "ADMIN_PASSWORD",), help="Create User")


    args = parser.parse_args()

    if args.list:
        review_system.list_media()
    elif args.user:
        user_name, password = args.user
        review_system.create_user(user_name, password)

    elif args.top_rated:
        category = args.top_rated[0]
        review_system.get_top_rated_media(category)

    elif args.subscribe:
        user_name, media_id = args.subscribe
        review_system.subscribe_to_media(user_name, media_id)
    elif args.add_media:
        user_name, media_type, media_name = args.add_media
        review_system.add_media(user_name, media_type, media_name)

    elif args.review:
            user_name, media_id, rating, comment = args.review
            review_system.submit_review(user_name, media_id, rating, comment)
    elif args.search:
        title = args.search[0]
        review_system.search(title)
    else:
        parser.print_help()
