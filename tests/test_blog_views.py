import pytest
from django.contrib.auth import get_user_model
from django.urls import reverse

from blog.forms import PostForm
from blog.models import Post

pytestmark = pytest.mark.django_db


@pytest.mark.parametrize("post_count", [0, 2])
def test_py_017_home_lists_all_posts(client, user, post_count):
    """PY-017: The public home view renders all posts, including the empty case."""
    for index in range(post_count):
        Post.objects.create(
            title=f"Post {index}",
            content=f"Content {index}",
            author=user,
        )

    response = client.get(reverse("blog-home"))

    assert response.status_code == 200
    assert "blog/home.html" in [template.name for template in response.templates]
    assert len(response.context["posts"]) == post_count
    assert list(response.context["posts"]) == list(Post.objects.all())


def test_py_018_about_renders_title_context(client):
    """PY-018: The About page renders with the documented title context."""
    response = client.get(reverse("blog-about"))

    assert response.status_code == 200
    assert "blog/about.html" in [template.name for template in response.templates]
    assert response.context["title"] == "About"
    assert "About Page !" in response.content.decode()


@pytest.mark.parametrize("post_exists", [True, False])
def test_py_019_post_detail_returns_post_or_404(client, user, post_exists):
    """PY-019: An existing post renders; an unknown integer ID returns 404."""
    if post_exists:
        post = Post.objects.create(
            title="Detail Post",
            content="Detail content",
            author=user,
        )
        response = client.get(reverse("detail", args=[post.pk]))

        assert response.status_code == 200
        assert "blog/post_detail.html" in [
            template.name for template in response.templates
        ]
        assert response.context["post"] == post
    else:
        response = client.get(reverse("detail", args=[999999]))

        assert response.status_code == 404


@pytest.mark.parametrize("method", ["get", "post"])
def test_py_020_anonymous_create_post_redirects_to_login(client, method):
    """PY-020: Anonymous GET and POST requests are redirected to login."""
    if method == "get":
        response = client.get(reverse("create_post"))
    else:
        response = client.post(
            reverse("create_post"),
            data={"title": "Anonymous", "content": "Should not be saved"},
        )

    assert response.status_code == 302
    assert response.url == f"{reverse('login')}?next={reverse('create_post')}"
    assert Post.objects.count() == 0


def test_py_021_authenticated_create_post_renders_empty_form(client, user):
    """PY-021: An authenticated GET receives the empty PostForm."""
    client.force_login(user)

    response = client.get(reverse("create_post"))

    assert response.status_code == 200
    assert "blog/create_post.html" in [
        template.name for template in response.templates
    ]
    assert isinstance(response.context["form"], PostForm)
    assert not response.context["form"].is_bound


def test_py_022_authenticated_create_post_saves_post_and_redirects(client, user):
    """PY-022: A valid authenticated POST saves the post and redirects home."""
    client.force_login(user)

    response = client.post(
        reverse("create_post"),
        data={"title": "New Post", "content": "New content"},
        follow=True,
    )

    assert response.redirect_chain == [(reverse("blog-home"), 302)]
    post = Post.objects.get()
    assert post.title == "New Post"
    assert post.content == "New content"
    assert post.author == user
    assert "The post has been created successfully." in response.content.decode()


@pytest.mark.parametrize(
    ("title", "is_valid"),
    [
        ("", False),
        ("T" * 101, False),
        ("T" * 100, True),
    ],
)
def test_py_023_create_post_handles_title_boundaries(client, user, title, is_valid):
    """PY-023: Invalid titles are not persisted; a 100-character title is valid."""
    client.force_login(user)

    response = client.post(
        reverse("create_post"),
        data={"title": title, "content": "Content"},
    )

    if is_valid:
        assert response.status_code == 302
        assert response.url == reverse("blog-home")
        assert Post.objects.count() == 1
    else:
        assert response.status_code == 200
        assert "blog/create_post.html" in [
            template.name for template in response.templates
        ]
        assert "title" in response.context["form"].errors
        assert Post.objects.count() == 0


def test_py_024_create_post_rejects_empty_content(client, user):
    """PY-024: Empty content is not persisted and the form is re-rendered."""
    client.force_login(user)

    response = client.post(
        reverse("create_post"),
        data={"title": "Valid title", "content": ""},
    )

    assert response.status_code == 200
    assert "blog/create_post.html" in [
        template.name for template in response.templates
    ]
    assert "content" in response.context["form"].errors
    assert Post.objects.count() == 0
