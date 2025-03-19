import pytest

def test_invalid_media_type(review_system):
    media_type = "invalid_media_type"
    result = review_system.get_top_rated_media(media_type)
    assert result == "[red]Error:[/red] Category must be movie, song or web_show"

@pytest.mark.parametrize(
    "media_type",
    [ "movie", "song", "web_show"],
    ids=[ "test_movie", "test_song", "test_web_show"],
)
def test_top_rated_media(review_system, media_type):
    medias, category = review_system.get_top_rated_media(media_type)
    assert category == media_type
    assert isinstance(medias, list)

