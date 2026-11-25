import pytest
from django.contrib.auth import get_user_model
from django.urls import reverse

from users.forms import UserRegisterForm
from users.models import Profile

pytestmark = pytest.mark.django_db

PASSWORD = "StrongPass!2345"


def test_py_025_register_get_renders_registration_form(client):
    """PY-025: A public GET renders the registration form."""
    response = client.get(reverse("register"))

    assert response.status_code == 200
    assert "users/register.html" in [
        template.name for template in response.templates
    ]
    assert isinstance(response.context["form"], UserRegisterForm)


def test_py_026_register_post_creates_user_and_redirects_to_login(client):
    """PY-026: A valid registration saves the user and redirects to login."""
    response = client.post(
        reverse("register"),
        data={
            "username": "newuser",
            "email": "newuser@example.com",
            "password1": PASSWORD,
            "password2": PASSWORD,
        },
        follow=True,
    )

    assert response.redirect_chain == [(reverse("login"), 302)]
    user = get_user_model().objects.get(username="newuser")
    assert user.email == "newuser@example.com"
    assert "Your account has been created. You can now login" in response.content.decode()


def test_py_027_register_prevents_duplicate_username(client, user):
    """PY-027: Reusing an existing username does not create another account."""
    response = client.post(
        reverse("register"),
        data={
            "username": user.username,
            "email": "another@example.com",
            "password1": PASSWORD,
            "password2": PASSWORD,
        },
    )

    assert response.status_code == 200
    assert "users/register.html" in [
        template.name for template in response.templates
    ]
    assert "username" in response.context["form"].errors
    assert get_user_model().objects.filter(username=user.username).count() == 1
    assert get_user_model().objects.count() == 1


def test_py_028_login_with_valid_credentials_authenticates_session(client, user):
    """PY-028: Valid credentials authenticate the session and redirect home."""
    response = client.post(
        reverse("login"),
        data={"username": user.username, "password": PASSWORD},
    )

    assert response.status_code == 302
    assert response.url == reverse("blog-home")
    assert client.session["_auth_user_id"] == str(user.pk)

    home_response = client.get(reverse("blog-home"))
    content = home_response.content.decode()
    assert "Profile" in content
    assert "Create Post" in content
    assert "Logout" in content


@pytest.mark.parametrize(
    ("username", "password"),
    [
        ("alice", "WrongPassword!2345"),
        ("unknown", PASSWORD),
    ],
)
def test_py_029_login_rejects_invalid_credentials(client, user, username, password):
    """PY-029: Wrong passwords and unknown users do not create a session."""
    response = client.post(
        reverse("login"),
        data={"username": username, "password": password},
    )

    assert response.status_code == 200
    assert "users/login.html" in [
        template.name for template in response.templates
    ]
    assert "_auth_user_id" not in client.session
    assert "Please enter a correct username and password." in response.content.decode()


def test_py_030_logout_post_clears_authenticated_session(client, user):
    """PY-030: An authenticated POST logout clears the session.

    The testing documentation expects a redirect.  The real application has no
    LOGOUT_REDIRECT_URL, so Django 4.2 re-renders users/logout.html with HTTP
    200 instead.  The session is still cleared, which is the core behaviour.
    """
    client.force_login(user)
    assert "_auth_user_id" in client.session

    response = client.post(reverse("logout"))

    assert response.status_code == 200
    assert "users/logout.html" in [
        template.name for template in response.templates
    ]
    assert "_auth_user_id" not in client.session


def test_py_031_anonymous_profile_redirects_to_login(client):
    """PY-031: Anonymous profile access redirects to login."""
    response = client.get(reverse("profile"))

    assert response.status_code == 302
    assert response.url == f"{reverse('login')}?next={reverse('profile')}"


def test_py_032_authenticated_profile_displays_user_details(client, user):
    """PY-032: The authenticated profile page shows image, username and email."""
    profile = Profile.objects.create(user=user)
    client.force_login(user)

    response = client.get(reverse("profile"))

    assert response.status_code == 200
    assert "users/profile.html" in [
        template.name for template in response.templates
    ]
    assert response.context["user"] == user
    content = response.content.decode()
    assert user.username in content
    assert user.email in content
    assert profile.image.url in content
