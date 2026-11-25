import pytest
from django.contrib.auth import get_user_model
from django.db.models.signals import post_save

from users.models import Profile

pytestmark = pytest.mark.django_db


def test_py_005_new_user_creates_exactly_one_profile():
    """PY-005: A newly created User automatically receives exactly one Profile.

    The documented behaviour is that the post-save receiver in
    ``users/signals.py`` runs automatically.  This test intentionally creates a
    User through the ORM without importing ``users.signals`` so that it
    verifies the real application wiring, not an isolated direct call.
    """
    user = get_user_model().objects.create_user(
        username="signaluser",
        email="signaluser@example.com",
        password="StrongPass!2345",
    )

    assert Profile.objects.filter(user=user).count() == 1


def test_py_006_saving_existing_user_does_not_create_second_profile():
    """PY-006: Re-saving an existing user does not duplicate the profile."""
    user = get_user_model().objects.create_user(
        username="existing",
        email="existing@example.com",
        password="StrongPass!2345",
    )
    # Precondition from the documentation: an existing user and profile.
    Profile.objects.create(user=user)

    # Import and call the receiver directly for the created=False branch.
    # Disconnect it immediately so the import does not change application
    # behaviour for other tests in this process.
    from users.signals import create_profile

    post_save.disconnect(create_profile, sender=get_user_model())
    try:
        create_profile(sender=get_user_model(), instance=user, created=False)
        user.save()
    finally:
        # Keep the receiver disconnected: the application never imports this
        # module, so this preserves the real runtime wiring for later tests.
        post_save.disconnect(create_profile, sender=get_user_model())

    assert Profile.objects.filter(user=user).count() == 1
