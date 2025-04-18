import pytest

def test_invalid_user(review_system):
    user = "invalid_username"
    media_cred = "5"
    rating = 4.3
    comment = "Some comment"
    result = review_system.submit_review(user, media_cred, rating, comment)
    assert result == "[red]Error:[/red] message : user_name not found"

def test_invalid_rating(review_system):
    user_name = "test_user"

    media_cred, rating, comment = "5", -1, "some comment"
    result = review_system.submit_review(user_name, media_cred, rating, comment )
    assert result == "[red]Error:[/red] : Rating must be between 1 and 5."

    media_cred, rating, comment = "5", 10, "some comment"
    result = review_system.submit_review(user_name, media_cred, rating, comment)
    assert result == "[red]Error:[/red] : Rating must be between 1 and 5."

def test_invalid_media_credential(review_system):
    user_name = "test_user"

    media_cred, rating, comment = "-1", 4.5, "some comment"
    result = review_system.submit_review(user_name, media_cred, rating, comment)
    assert result == f"[red]Error:[/red] message : media not found"

    media_cred, rating, comment = "invalid_media_name", 4.5, "some comment"
    result = review_system.submit_review(user_name, media_cred, rating, comment)
    assert result == f"[red]Error:[/red] message : media not found"

def test_review_submission(review_system):
    user_name = "test_user"
    media_cred, rating, comment = "1", 4.3, "some comment"
    result = review_system.submit_review(user_name, "1", 4.3, "some comment")

    assert result == f"[green]Review added by \nUser : {user_name}\nMedia : {media_cred}, Rating : {rating},\nComment : {comment}[/green]"

