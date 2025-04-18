import pytest
from unittest import mock

def test_list_media_success(review_system):
    result = review_system.list_media()
    assert isinstance(result, list)

@mock.patch('src.review_system.ReviewSystem.list_media')
def test_list_media_fail(mock_list_media, review_system):
    mock_list_media.return_value = "Error in DB"
    assert review_system.list_media() == "Error in DB"