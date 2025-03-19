import time

import pytest
import os
import sqlite3

from src.review_system import ReviewSystem

@pytest.fixture(scope="module")
def review_system():
    yield ReviewSystem()
    #
    # try:
    #     with sqlite3.connect("media.db") as conn:
    #         conn.close()
    #     print("Database connection manually closed before teardown.")
    # except Exception as e:
    #     print(f"Error closing database connection: {e}")
    #
    # file_name = "media.db"  # FIX: Directly refer to media.db instead of tests/media.db
    # print(f"Checking file at: {os.path.abspath(file_name)}")
    # abs_path = os.path.abspath(file_name)
    # print(f"Current working directory: {os.getcwd()}")  # Ensure it's inside `tests/`
    # time.sleep(1)
    # os.remove(abs_path)
    # # print(f"{file_name} deleted successfully.")
