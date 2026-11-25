import os

import pytest

# pytest-playwright's synchronous driver runs an asyncio event loop in the main
# thread.  Django 4.2 blocks synchronous ORM calls from such a context during
# test-database setup, so the documented test-only escape hatch is enabled.
os.environ.setdefault("DJANGO_ALLOW_ASYNC_UNSAFE", "true")

# The application's base template loads Bootstrap, jQuery and Popper from
# public CDNs.  In this execution environment maxcdn.bootstrapcdn.com and
# code.jquery.com cannot be resolved, while jsDelivr is reachable.  The
# rewrites below request the same library versions from an equivalent CDN so
# the browser tests can exercise the application's real Bootstrap layout and
# JavaScript behaviour.  No application file is modified.
CDN_REWRITES = {
    "https://maxcdn.bootstrapcdn.com/bootstrap/4.0.0/css/bootstrap.min.css": (
        "https://cdn.jsdelivr.net/npm/bootstrap@4.0.0/dist/css/bootstrap.min.css"
    ),
    "https://maxcdn.bootstrapcdn.com/bootstrap/4.0.0/js/bootstrap.min.js": (
        "https://cdn.jsdelivr.net/npm/bootstrap@4.0.0/dist/js/bootstrap.min.js"
    ),
    "https://code.jquery.com/jquery-3.2.1.slim.min.js": (
        "https://cdn.jsdelivr.net/npm/jquery@3.2.1/dist/jquery.slim.min.js"
    ),
    "https://cdnjs.cloudflare.com/ajax/libs/popper.js/1.12.9/umd/popper.min.js": (
        "https://cdn.jsdelivr.net/npm/popper.js@1.12.9/dist/umd/popper.min.js"
    ),
}


@pytest.fixture(autouse=True)
def rewrite_unreachable_cdn_assets(page):
    for original, replacement in CDN_REWRITES.items():
        page.route(
            original,
            lambda route, request, target=replacement: route.continue_(url=target),
        )
    yield
