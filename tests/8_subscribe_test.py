import pytest

def test_invalid_username(review_system):
    user_name = "invalid_username"
    media_cred = "demo1"
    result = review_system.subscribe_to_media(user_name, media_cred)
    assert result == f"[red]Error:[/red] Failed to subscribe. Message : user_name does not exist!"

def test_invalid_media_credential(review_system):
    user_name = "test_user"
    media_cred = "invalid_media"
    result = review_system.subscribe_to_media(user_name, media_cred)
    assert result == f"[red]Error:[/red] Failed to subscribe. Message : media not available!"

@pytest.mark.parametrize(
    "user_name, media_cred",
    [
        ("test_user", "demo1"),
        ("test_user", "demo2"),
        ("test_user", "3"),
    ],
    ids=["subscribe-with-media-name-1", "subscribe-with-media-name-2", "subscribe-with-media-id"]
)
def test_subscribe(review_system, user_name, media_cred):
    result = review_system.subscribe_to_media(user_name, media_cred)
    assert result == f"[green]User : {user_name}, added as a subscriber to media : {media_cred}[/green]"

@pytest.mark.parametrize(
    "user_name, media_cred",
    [
        ("test_user", "demo1"),
        ("test_user", "2"),
        ("test_user", "demo3"),
    ]
)
def test_already_subscribed(review_system, user_name, media_cred):
    result = review_system.subscribe_to_media(user_name, media_cred)
    assert result == "[red]Error:[/red] Failed to subscribe. Message : user already subscribed!"


