import pytest

def test_invalid_media_credential(review_system):
    media_cred = "-1"
    result = review_system.search(media_cred)
    assert result == f"[red]Error:[/red] Search Error, message : Media not found"

    media_cred = "invalid_media"
    result = review_system.search(media_cred)
    assert result == f"[red]Error:[/red] Search Error, message : Media not found"


@pytest.mark.parametrize(
    "media_cred",
    [
        "demo1",
        "demo2",
        "demo3"
    ],
    ids=["test1", "test2", "test3"]
)
def test_search_media(review_system, media_cred):
    result = review_system.search(media_cred)
    reviews, media = result
    assert isinstance(reviews, list)
    assert media == media_cred
