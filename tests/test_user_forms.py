import pytest
from django.contrib.auth import get_user_model

from users.forms import UserRegisterForm

pytestmark = pytest.mark.django_db

VALID_PASSWORD = "StrongPass!2345"


def registration_data(**overrides):
    data = {
        "username": "newuser",
        "email": "newuser@example.com",
        "password1": VALID_PASSWORD,
        "password2": VALID_PASSWORD,
    }
    data.update(overrides)
    return data


def test_py_012_user_register_form_accepts_valid_data_and_saves_user():
    """PY-012: Valid registration data produces a valid form and a saved User."""
    form = UserRegisterForm(data=registration_data())

    assert form.is_valid(), form.errors

    saved_user = form.save()

    assert saved_user.pk is not None
    assert saved_user.username == "newuser"
    assert saved_user.email == "newuser@example.com"
    assert get_user_model().objects.filter(username="newuser").count() == 1


def test_py_013_user_register_form_rejects_existing_username():
    """PY-013: A duplicate username is rejected."""
    get_user_model().objects.create_user(
        username="existing",
        email="existing@example.com",
        password=VALID_PASSWORD,
    )

    form = UserRegisterForm(data=registration_data(username="existing"))

    assert not form.is_valid()
    assert "username" in form.errors
    assert "already exists" in str(form.errors["username"])


def test_py_014_user_register_form_rejects_mismatched_passwords():
    """PY-014: Different password1 and password2 values are rejected."""
    form = UserRegisterForm(
        data=registration_data(password1=VALID_PASSWORD, password2="DifferentPass!2345")
    )

    assert not form.is_valid()
    assert "password2" in form.errors
    assert "match" in str(form.errors["password2"])


@pytest.mark.parametrize("email", ["", "not-an-email"])
def test_py_015_user_register_form_validates_email(email):
    """PY-015: Empty or malformed email addresses are rejected."""
    form = UserRegisterForm(data=registration_data(email=email))

    assert not form.is_valid()
    assert "email" in form.errors


@pytest.mark.parametrize(
    "password",
    [
        "Ab1!",  # Too short (minimum length is 8).
        "12345678",  # Entirely numeric.
        "password",  # Common password.
        "alice123",  # Too similar to the username (and exactly 8 characters).
    ],
)
def test_py_016_user_register_form_rejects_weak_passwords(password):
    """PY-016: Django password validators reject weak passwords."""
    form = UserRegisterForm(
        data=registration_data(
            username="alice",
            email="alice@example.com",
            password1=password,
            password2=password,
        )
    )

    assert not form.is_valid()
    assert "password2" in form.errors
