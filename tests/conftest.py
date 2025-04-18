import time

import pytest
import os
import sqlite3

from src.review_system import ReviewSystem

@pytest.fixture(scope="session")
def review_system():
    file_name = "test_media.db"  # Replace with the actual filename
    if os.path.exists(file_name):
        os.remove(file_name)

    system = ReviewSystem("test_media.db")

    yield system

    system.redis_client.flushall()