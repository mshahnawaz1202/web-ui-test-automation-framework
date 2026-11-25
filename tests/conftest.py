import pytest
from django.contrib.auth import get_user_model

PASSWORD = "StrongPass!2345"


@pytest.fixture
def user(db):
    """A normal registered user used by isolated Pytest tests."""
    return get_user_model().objects.create_user(
        username="alice",
        email="alice@example.com",
        password=PASSWORD,
    )


@pytest.fixture
def other_user(db):
    """A second user, useful for cascade and ownership assertions."""
    return get_user_model().objects.create_user(
        username="bob",
        email="bob@example.com",
        password=PASSWORD,
    )
