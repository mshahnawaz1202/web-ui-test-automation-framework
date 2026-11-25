import pytest
from django.contrib.auth import get_user_model
from playwright.sync_api import expect

from blog.models import Post
from users.models import Profile

pytestmark = [pytest.mark.ui, pytest.mark.django_db(transaction=True)]

PASSWORD = "StrongPass!2345"


def create_user(
    username="shahnawaz", email=None, password=PASSWORD, with_profile=False
):
    user = get_user_model().objects.create_user(
        username=username,
        email=email or f"{username}@example.com",
        password=password,
    )
    if with_profile:
        # users.signals.create_profile already creates the profile when the
        # user is saved, so only ensure it exists instead of duplicating it.
        Profile.objects.get_or_create(user=user)
    return user


def goto(page, live_server, path):
    return page.goto(f"{live_server.url}{path}")


def login_via_ui(page, live_server, username="shahnawaz", password=PASSWORD):
    goto(page, live_server, "/login/")
    page.locator("#id_username").fill(username)
    page.locator("#id_password").fill(password)
    page.get_by_role("button", name="Login").click()
    expect(page).to_have_url(f"{live_server.url}/")


def display_date(value):
    return value.strftime("%B %d, %Y")


# ---------------------------------------------------------------------------
# UI-001 / UI-002: Home listing
# ---------------------------------------------------------------------------


def test_ui_001_home_listing_shows_posts_and_opens_detail(page, live_server):
    user = create_user("shahnawaz")
    post = Post.objects.create(
        title="First Post",
        content="First content",
        author=user,
    )

    response = goto(page, live_server, "/")

    assert response.status == 200
    expect(page.locator("nav.navbar")).to_be_visible()
    expect(page.get_by_role("link", name="Django Blog")).to_be_visible()
    expect(page.get_by_role("link", name="Home")).to_be_visible()
    expect(page.get_by_role("link", name="About", exact=True)).to_be_visible()
    expect(page.get_by_role("link", name="Login", exact=True)).to_be_visible()
    expect(page.get_by_role("link", name="Register", exact=True)).to_be_visible()
    expect(page.locator("article.media")).to_have_count(1)
    expect(page.locator("h2 a.article-title")).to_have_text("First Post")
    expect(page.locator(".article-content")).to_have_text("First content")
    expect(page.locator(".article-metadata")).to_contain_text("shahnawaz")
    expect(page.locator(".article-metadata")).to_contain_text(
        display_date(post.date_posted)
    )
    expect(page.get_by_text("Our Sidebar")).to_be_visible()

    page.locator("h2 a.article-title").click()

    expect(page).to_have_url(f"{live_server.url}/detail/{post.pk}/")
    expect(page.locator("h2 a.article-title")).to_have_text("First Post")
    expect(page.locator(".article-content")).to_have_text("First content")


def test_ui_001_home_mobile_navbar_toggle(page, live_server):
    page.set_viewport_size({"width": 375, "height": 812})
    goto(page, live_server, "/")

    toggler = page.locator("button.navbar-toggler")
    menu = page.locator("#navbarText")

    expect(toggler).to_be_visible()
    expect(menu).not_to_be_visible()

    toggler.click()

    expect(menu).to_be_visible()


def test_ui_002_home_empty_state(page, live_server):
    response = goto(page, live_server, "/")

    assert response.status == 200
    expect(page.locator("article.media")).to_have_count(0)
    expect(page.locator("nav.navbar")).to_be_visible()
    expect(page.get_by_text("Our Sidebar")).to_be_visible()

    page.get_by_role("link", name="About", exact=True).click()

    expect(page).to_have_url(f"{live_server.url}/about/")


# ---------------------------------------------------------------------------
# UI-003: About
# ---------------------------------------------------------------------------


def test_ui_003_about_page_and_navigation(page, live_server):
    response = goto(page, live_server, "/about/")

    assert response.status == 200
    expect(page.get_by_role("heading", name="About Page !")).to_be_visible()

    page.get_by_role("link", name="Home").click()
    expect(page).to_have_url(f"{live_server.url}/")

    page.get_by_role("link", name="About", exact=True).click()
    expect(page.get_by_role("heading", name="About Page !")).to_be_visible()


# ---------------------------------------------------------------------------
# UI-004: Registration
# ---------------------------------------------------------------------------


def test_ui_004_registration_with_valid_data(page, live_server):
    goto(page, live_server, "/register/")

    expect(page.get_by_text("Join Today")).to_be_visible()
    page.locator("#id_username").fill("hamza")
    page.locator("#id_email").fill("hamza@example.com")
    page.locator("#id_password1").fill(PASSWORD)
    page.locator("#id_password2").fill(PASSWORD)
    page.get_by_role("button", name="Sign Up").click()

    expect(page).to_have_url(f"{live_server.url}/login/")
    expect(page.locator(".alert-success")).to_contain_text(
        "Your account has been created"
    )
    assert get_user_model().objects.filter(username="hamza").count() == 1


def test_ui_004_registration_page_links_to_login(page, live_server):
    goto(page, live_server, "/register/")

    page.get_by_role("link", name="Sign In").click()

    expect(page).to_have_url(f"{live_server.url}/login/")


def test_ui_004_registration_rejects_duplicate_username(page, live_server):
    create_user("existing", "existing@example.com")
    goto(page, live_server, "/register/")

    page.locator("#id_username").fill("existing")
    page.locator("#id_email").fill("another@example.com")
    page.locator("#id_password1").fill(PASSWORD)
    page.locator("#id_password2").fill(PASSWORD)
    page.get_by_role("button", name="Sign Up").click()

    expect(page).to_have_url(f"{live_server.url}/register/")
    expect(page.locator("body")).to_contain_text(
        "A user with that username already exists."
    )
    assert get_user_model().objects.filter(username="existing").count() == 1


def test_ui_004_registration_rejects_password_mismatch(page, live_server):
    goto(page, live_server, "/register/")

    page.locator("#id_username").fill("hamza")
    page.locator("#id_email").fill("hamza@example.com")
    page.locator("#id_password1").fill(PASSWORD)
    page.locator("#id_password2").fill("DifferentPass!2345")
    page.get_by_role("button", name="Sign Up").click()

    expect(page).to_have_url(f"{live_server.url}/register/")
    expect(page.locator("body")).to_contain_text("The two password fields")
    assert get_user_model().objects.count() == 0


def test_ui_004_registration_rejects_invalid_email(page, live_server):
    goto(page, live_server, "/register/")

    page.locator("#id_username").fill("hamza")
    page.locator("#id_email").fill("a@b")
    page.locator("#id_password1").fill(PASSWORD)
    page.locator("#id_password2").fill(PASSWORD)
    page.get_by_role("button", name="Sign Up").click()

    expect(page).to_have_url(f"{live_server.url}/register/")
    expect(page.locator("body")).to_contain_text("Enter a valid email address.")
    assert get_user_model().objects.count() == 0


def test_ui_004_registration_rejects_weak_password(page, live_server):
    goto(page, live_server, "/register/")

    page.locator("#id_username").fill("hamza")
    page.locator("#id_email").fill("hamza@example.com")
    page.locator("#id_password1").fill("123")
    page.locator("#id_password2").fill("123")
    page.get_by_role("button", name="Sign Up").click()

    expect(page).to_have_url(f"{live_server.url}/register/")
    expect(page.locator("body")).to_contain_text("at least 8 characters")
    assert get_user_model().objects.count() == 0


# ---------------------------------------------------------------------------
# UI-005: Login
# ---------------------------------------------------------------------------


def test_ui_005_login_with_valid_credentials(page, live_server):
    create_user("shahnawaz")
    goto(page, live_server, "/login/")

    page.locator("#id_username").fill("shahnawaz")
    page.locator("#id_password").fill(PASSWORD)
    page.get_by_role("button", name="Login").click()

    expect(page).to_have_url(f"{live_server.url}/")
    expect(page.get_by_role("link", name="Profile", exact=True)).to_be_visible()
    expect(page.get_by_role("link", name="Create Post", exact=True)).to_be_visible()
    expect(page.get_by_role("link", name="Logout", exact=True)).to_be_visible()
    expect(page.get_by_role("link", name="Login", exact=True)).to_have_count(0)
    expect(page.get_by_role("link", name="Register", exact=True)).to_have_count(0)


@pytest.mark.parametrize(
    ("username", "password"),
    [
        ("shahnawaz", "WrongPassword!2345"),
        ("unknown", PASSWORD),
    ],
)
def test_ui_005_login_rejects_invalid_credentials(
    page, live_server, username, password
):
    create_user("shahnawaz")
    goto(page, live_server, "/login/")

    page.locator("#id_username").fill(username)
    page.locator("#id_password").fill(password)
    page.get_by_role("button", name="Login").click()

    expect(page).to_have_url(f"{live_server.url}/login/")
    expect(page.locator("body")).to_contain_text(
        "Please enter a correct username and password."
    )
    expect(page.get_by_role("link", name="Login", exact=True)).to_be_visible()


def test_ui_005_login_page_links_to_register(page, live_server):
    goto(page, live_server, "/login/")

    page.get_by_role("link", name="Sign Up").click()

    expect(page).to_have_url(f"{live_server.url}/register/")


# ---------------------------------------------------------------------------
# UI-006: Logout
# ---------------------------------------------------------------------------


def test_ui_006_logout_via_navbar_link(page, live_server):
    create_user("shahnawaz")
    login_via_ui(page, live_server)

    page.get_by_role("link", name="Logout", exact=True).click()

    expect(page).to_have_url(f"{live_server.url}/logout/")
    expect(
        page.get_by_role("heading", name="You have been logged out !")
    ).to_be_visible()
    expect(page.get_by_role("link", name="Login Again")).to_be_visible()
    expect(page.get_by_role("link", name="Login", exact=True)).to_be_visible()
    expect(page.get_by_role("link", name="Register", exact=True)).to_be_visible()

    page.get_by_role("link", name="Login Again").click()
    expect(page).to_have_url(f"{live_server.url}/login/")


# ---------------------------------------------------------------------------
# UI-007: Blog detail
# ---------------------------------------------------------------------------


def test_ui_007_existing_post_detail(page, live_server):
    user = create_user("shahnawaz")
    post = Post.objects.create(
        title="Detail Post",
        content="Detail content",
        author=user,
    )
    goto(page, live_server, "/")

    page.get_by_role("link", name="Detail Post").click()

    expect(page).to_have_url(f"{live_server.url}/detail/{post.pk}/")
    expect(page.locator("h2 a.article-title")).to_have_text("Detail Post")
    expect(page.locator(".article-content")).to_have_text("Detail content")
    expect(page.locator(".article-metadata")).to_contain_text("shahnawaz")
    expect(page.locator(".article-metadata")).to_contain_text(
        display_date(post.date_posted)
    )
    expect(page.locator("article.media img")).to_have_count(1)


def test_ui_007_unknown_post_shows_404_with_home_link(page, live_server):
    response = goto(page, live_server, "/detail/999999/")

    assert response.status == 404
    expect(page.locator("body")).to_contain_text("Not Found")
    expect(page.locator("article.media")).to_have_count(0)
    # The testing documentation expects the 404 page to keep a Home link.
    expect(page.get_by_role("link", name="Home")).to_be_visible()


# ---------------------------------------------------------------------------
# UI-008: Create post
# ---------------------------------------------------------------------------


def test_ui_008_create_post_with_valid_data(page, live_server):
    create_user("shahnawaz")
    login_via_ui(page, live_server)
    goto(page, live_server, "/create-post/")

    expect(page.get_by_role("heading", name="Create Post")).to_be_visible()
    page.locator("#id_title").fill("UI Post")
    page.locator("#id_content").fill("UI content")
    page.get_by_role("button", name="Save").click()

    expect(page).to_have_url(f"{live_server.url}/")
    expect(page.locator(".alert-success")).to_contain_text(
        "The post has been created successfully."
    )
    expect(page.locator("h2 a.article-title")).to_have_text("UI Post")
    assert (
        Post.objects.filter(title="UI Post", author__username="shahnawaz").count()
        == 1
    )


def test_ui_008_create_post_rejects_empty_fields(page, live_server):
    create_user("shahnawaz")
    login_via_ui(page, live_server)
    goto(page, live_server, "/create-post/")

    page.get_by_role("button", name="Save").click()

    expect(page).to_have_url(f"{live_server.url}/create-post/")
    assert page.locator("#id_title").evaluate("element => element.validity.valueMissing")
    assert page.locator("#id_content").evaluate(
        "element => element.validity.valueMissing"
    )
    assert Post.objects.count() == 0


def test_ui_008_create_post_rejects_overlong_title(page, live_server):
    create_user("shahnawaz")
    login_via_ui(page, live_server)
    goto(page, live_server, "/create-post/")

    expect(page.locator("#id_title")).to_have_attribute("maxlength", "100")
    page.locator("#id_title").evaluate(
        "(element, value) => { element.value = value; "
        "element.dispatchEvent(new Event('input', { bubbles: true })); }",
        "T" * 101,
    )
    page.locator("#id_content").fill("Content")
    page.get_by_role("button", name="Save").click()

    expect(page).to_have_url(f"{live_server.url}/create-post/")
    title = page.locator("#id_title")
    validation_message = title.evaluate("element => element.validationMessage")
    body_text = page.locator("body").inner_text()
    assert "100" in validation_message or "100 characters" in body_text
    assert Post.objects.count() == 0


def test_ui_008_create_post_requires_login(page, live_server):
    response = goto(page, live_server, "/create-post/")

    assert response.status == 200
    expect(page).to_have_url(f"{live_server.url}/login/?next=/create-post/")
    expect(page.get_by_text("Login Here")).to_be_visible()
    assert Post.objects.count() == 0


# ---------------------------------------------------------------------------
# UI-009: Profile
# ---------------------------------------------------------------------------


def test_ui_009_profile_displays_authenticated_user(page, live_server):
    user = create_user("shahnawaz", with_profile=True)
    login_via_ui(page, live_server)
    goto(page, live_server, "/profile/")

    expect(page.locator("h2.account-heading")).to_have_text("shahnawaz")
    expect(page.locator("p.text-secondary")).to_have_text("shahnawaz@example.com")
    image = page.locator("img.account-img")
    expect(image).to_be_visible()
    assert "default.png" in image.get_attribute("src")


def test_ui_009_profile_requires_login(page, live_server):
    goto(page, live_server, "/profile/")

    expect(page).to_have_url(f"{live_server.url}/login/?next=/profile/")
    expect(page.get_by_text("Login Here")).to_be_visible()


# ---------------------------------------------------------------------------
# UI-010: Shared responsive navigation
# ---------------------------------------------------------------------------


def test_ui_010_navigation_reflects_authentication_state(page, live_server):
    goto(page, live_server, "/")

    expect(page.get_by_role("link", name="Login", exact=True)).to_be_visible()
    expect(page.get_by_role("link", name="Register", exact=True)).to_be_visible()
    expect(page.get_by_role("link", name="Profile", exact=True)).to_have_count(0)
    expect(page.get_by_role("link", name="Create Post", exact=True)).to_have_count(0)
    expect(page.get_by_role("link", name="Logout", exact=True)).to_have_count(0)

    create_user("shahnawaz", with_profile=True)
    login_via_ui(page, live_server)

    expect(page.get_by_role("link", name="Profile", exact=True)).to_be_visible()
    expect(page.get_by_role("link", name="Create Post", exact=True)).to_be_visible()
    expect(page.get_by_role("link", name="Logout", exact=True)).to_be_visible()
    expect(page.get_by_role("link", name="Login", exact=True)).to_have_count(0)
    expect(page.get_by_role("link", name="Register", exact=True)).to_have_count(0)

    page.get_by_role("link", name="Profile", exact=True).click()
    expect(page).to_have_url(f"{live_server.url}/profile/")

    page.get_by_role("link", name="Create Post", exact=True).click()
    expect(page).to_have_url(f"{live_server.url}/create-post/")

    page.get_by_role("link", name="Home").click()
    expect(page).to_have_url(f"{live_server.url}/")


def test_ui_010_mobile_navigation_toggle_and_link(page, live_server):
    page.set_viewport_size({"width": 375, "height": 812})
    goto(page, live_server, "/")

    toggler = page.locator("button.navbar-toggler")
    menu = page.locator("#navbarText")

    expect(toggler).to_be_visible()
    expect(menu).not_to_be_visible()

    toggler.click()
    expect(menu).to_be_visible()

    page.get_by_role("link", name="About", exact=True).click()
    expect(page.get_by_role("heading", name="About Page !")).to_be_visible()
