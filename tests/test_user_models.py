import pytest

from users.models import Profile

pytestmark = pytest.mark.django_db


def test_py_004_profile_str_returns_username_profile(user):
    """PY-004: Profile.__str__ returns '<username> Profile'."""
    profile = Profile.objects.create(user=user)

    assert str(profile) == "alice Profile"
