import pytest
import os
from dotenv import load_dotenv

load_dotenv()

def test_wrong_password(review_system):
        user_name = "test_user"
        result = review_system.create_user(user_name, "wrong_password")
        assert result == "[red]Error:[/red] Wrong Password"


def test_create_user(review_system):
    user_name = "test_user"
    password = os.getenv("admin_password")
    result = review_system.create_user(user_name, password)
    assert result == f"[green]User created with user_name : {user_name}[/green]"

def test_existing_user(review_system):
    user_name = "test_user"
    password = os.getenv("admin_password")
    result = review_system.create_user(user_name, password)
    assert result == f"[red]Error:[/red] Same user_name already exists : {user_name}"
