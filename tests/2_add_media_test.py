import pytest

from src.medias import Movie, MediaFactory


def test_username(review_system):
    user_name = "invalid_username"
    media_type = "movie"
    media_name = "Demo"
    result = review_system.add_media(MediaFactory.create_media(user_name, media_type, media_name))
    assert result == f"[red]Error:[/red] Add Media error, message : User does not exist"

def test_media_type(review_system):
    user_name = "test_user"
    media_type = "invalid_media_type"
    media_name = "Demo"
    result = review_system.add_media(MediaFactory.create_media(user_name, media_type, media_name))
    assert result == "[red]Error:[/red] Media Type must be movie, song or web_show"

@pytest.mark.parametrize(
    "user_name, media_type, media_name",
    [
        ("test_user", "movie", "Demo1"),
        ("test_user", "song", "demo2"),
        ("test_user", "web_show", "demo3"),
    ],
    ids=["movie", "song", "wbe_show"]

)
def test_adding_media(review_system, user_name, media_type, media_name):
    result = review_system.add_media(MediaFactory.create_media(user_name, media_type, media_name))
    assert result == f"[green]Media added \nType : {media_type}, \nName : {media_name}[/green]"

# def test_duplicate_media(review_system):
#     user_name = "test_user"
#     media_type = "movie"
#     media_name = "Demo"
#     result = review_system.add_media(MediaFactory.create_media(user_name, media_type, media_name))
#     assert result == "[red]Error:[/red] Media Type must be movie, song or web_show"
