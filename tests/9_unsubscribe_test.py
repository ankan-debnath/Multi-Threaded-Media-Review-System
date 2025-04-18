import pytest

def test_invalid_username(review_system):
    user_name = "invalid_username"
    media_cred = "demo1"
    result = review_system.unsubscribe_to_media(user_name, media_cred)
    assert result == f"[red]Error:[/red] Failed to unsubscribe. Message : user_name does not exist!"

def test_invalid_media_credential(review_system):
    user_name = "test_user"
    media_cred = "invalid_media"
    result = review_system.unsubscribe_to_media(user_name, media_cred)
    assert result == f"[red]Error:[/red] Failed to unsubscribe. Message : media not available!"

@pytest.mark.parametrize(
    "user_name, media_cred",
    [
        ("test_user", "demo1"),
        ("test_user", "demo2"),
        ("test_user", "3"),
    ],
    ids=["unsubscribe-with-media-name-1", "unsubscribe-with-media-name-2", "unsubscribe-with-media-id"]
)
def test_unsubscribe(review_system, user_name, media_cred):
    result = review_system.unsubscribe_to_media(user_name, media_cred)
    assert result == f"[green]User : {user_name}, unsubscribed from media : {media_cred}[/green]"

# @pytest.mark.parametrize(
#     "user_name, media_cred",
#     [
#         ("test_user", "demo1"),
#         ("test_user", "2"),
#         ("test_user", "demo3"),
#     ]
# )
# def test_already_unsubscribed(review_system, user_name, media_cred):
#     result = review_system.subscribe_to_media(user_name, media_cred)
#     assert result == "[red]Error:[/red] Failed to unsubscribe. Message : user already unsubscribed!"


