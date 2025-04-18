import pytest

def test_invalid_username(review_system):
    user_name = "invalid_username"
    media_type = "movie"
    result = review_system.get_recommendation_with_category(user_name, media_type)
    assert result == f"[red]Error:[/red] recommendation error : user_name does not exist!"

def test_invalid_media_type(review_system):
    user_name = "test_user"
    media_type = "invalid_media_type"
    result = review_system.get_recommendation_with_category(user_name, media_type)
    assert result == "[red]Error:[/red] Media Type must be movie, song or web_show"

@pytest.mark.parametrize(
    "user_name, media_type",
    [
        ("test_user", "movie"),
        ("test_user", "song"),
        ("test_user", "web_show"),
        ("test_user", "")
    ],
    ids=["recommend_movie", "recommend_song", "recommend_web_show", "general"]
)
def test_recommend_user(review_system, user_name, media_type):
    final_recommendations, user, category = review_system.get_recommendation_with_category(user_name, media_type)
    assert user_name == user
    assert media_type == category
    assert isinstance(final_recommendations, list)

