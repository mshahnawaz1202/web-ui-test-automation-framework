import pytest

from blog.forms import PostForm

pytestmark = pytest.mark.django_db


def test_py_007_post_form_accepts_valid_data_and_exposes_expected_fields():
    """PY-007: PostForm is valid and exposes only title and content."""
    form = PostForm(data={"title": "Valid post", "content": "Valid content"})

    assert form.is_valid(), form.errors
    assert list(form.fields) == ["title", "content"]
    assert form.cleaned_data["title"] == "Valid post"
    assert form.cleaned_data["content"] == "Valid content"


def test_py_008_post_form_rejects_missing_title():
    """PY-008: An empty title is invalid; a one-character title is valid."""
    empty_form = PostForm(data={"title": "", "content": "Content"})

    assert not empty_form.is_valid()
    assert "title" in empty_form.errors

    boundary_form = PostForm(data={"title": "T", "content": "Content"})
    assert boundary_form.is_valid(), boundary_form.errors


def test_py_009_post_form_rejects_missing_content():
    """PY-009: Empty content is invalid; one-character content is valid."""
    empty_form = PostForm(data={"title": "Valid title", "content": ""})

    assert not empty_form.is_valid()
    assert "content" in empty_form.errors

    boundary_form = PostForm(data={"title": "Valid title", "content": "C"})
    assert boundary_form.is_valid(), boundary_form.errors


def test_py_010_post_form_accepts_100_character_title():
    """PY-010: A title at the maximum length of 100 is valid."""
    form = PostForm(data={"title": "T" * 100, "content": "Content"})

    assert form.is_valid(), form.errors


def test_py_011_post_form_rejects_101_character_title():
    """PY-011: A title one character over the limit is invalid."""
    form = PostForm(data={"title": "T" * 101, "content": "Content"})

    assert not form.is_valid()
    assert "title" in form.errors
    assert "100 characters" in str(form.errors["title"])
