import pytest

from src.review_system import ReviewSystem

@pytest.fixture(scope="module")
def review_system():
    yield ReviewSystem()
