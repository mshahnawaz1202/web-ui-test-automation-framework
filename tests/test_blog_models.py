import pytest
from django.contrib.auth import get_user_model

from blog.models import Post

pytestmark = pytest.mark.django_db


def test_py_001_post_str_returns_title(user):
    """PY-001: Post.__str__ returns the saved post title."""
    post = Post.objects.create(
        title="Test Post",
        content="Some content",
        author=user,
    )

    assert str(post) == "Test Post"


def test_py_002_post_str_returns_maximum_length_title(user):
    """PY-002: Post.__str__ returns a complete 100-character title."""
    title = "T" * 100
    post = Post.objects.create(
        title=title,
        content="Some content",
        author=user,
    )

    assert str(post) == title
    assert len(str(post)) == 100


def test_py_003_deleting_author_cascades_to_posts(user, other_user):
    """PY-003: Deleting a post author deletes every post owned by that author."""
    Post.objects.create(title="First", content="First content", author=user)
    Post.objects.create(title="Second", content="Second content", author=user)

    assert Post.objects.count() == 2

    user.delete()

    assert Post.objects.count() == 0
    # An unrelated user with no posts remains valid.
    assert get_user_model().objects.filter(pk=other_user.pk).exists()
