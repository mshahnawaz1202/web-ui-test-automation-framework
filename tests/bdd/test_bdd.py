import pytest
from django.contrib.auth import get_user_model
from pytest_bdd import given, parsers, scenario, then, when

from blog.models import Post
from users.models import Profile

pytestmark = [pytest.mark.django_db, pytest.mark.bdd]

PASSWORD = "StrongPass!2345"


@pytest.fixture
def context():
    return {}


def make_user(username="alice", email=None, password=PASSWORD):
    return get_user_model().objects.create_user(
        username=username,
        email=email or f"{username}@example.com",
        password=password,
    )


def registration_payload(**overrides):
    data = {
        "username": "newuser",
        "email": "newuser@example.com",
        "password1": PASSWORD,
        "password2": PASSWORD,
    }
    data.update(overrides)
    return data


# ---------------------------------------------------------------------------
# BDD-001 .. BDD-004: User registration
# ---------------------------------------------------------------------------


@scenario("features/registration.feature", "A visitor registers with valid details")
def test_bdd_001_register_new_user():
    pass


@scenario(
    "features/registration.feature",
    "Registration rejects an existing username",
)
def test_bdd_002_reject_duplicate_username():
    pass


@scenario(
    "features/registration.feature",
    "Registration rejects password mismatch",
)
def test_bdd_003_reject_password_mismatch():
    pass


@scenario(
    "features/registration.feature",
    "Registration validates email format",
)
def test_bdd_004_validate_email():
    pass


@given('the visitor is on "/register/"')
def visitor_on_register(client, context):
    context["response"] = client.get("/register/")
    assert context["response"].status_code == 200


@given('a user with the username "existing" already exists')
def existing_user_exists():
    make_user("existing")


@when(
    "the visitor enters a unique username, a valid email, and matching strong "
    "passwords, then selects Sign Up"
)
def submit_valid_registration(client, context):
    context["response"] = client.post("/register/", data=registration_payload())


@when("the visitor submits the existing username with otherwise valid data")
def submit_duplicate_registration(client, context):
    context["response"] = client.post(
        "/register/",
        data=registration_payload(username="existing"),
    )


@when("the visitor enters two different passwords and submits")
def submit_mismatched_registration(client, context):
    context["response"] = client.post(
        "/register/",
        data=registration_payload(
            password1=PASSWORD,
            password2="DifferentPass!2345",
        ),
    )


@when(
    parsers.re(
        r'the visitor submits the email "(?P<email>.*)" with otherwise valid data'
    )
)
def submit_email_registration(client, context, email):
    context["response"] = client.post(
        "/register/",
        data=registration_payload(email=email),
    )


@then('a user account is created and the visitor is redirected to "/login/"')
def account_created_and_redirected(client, context):
    assert get_user_model().objects.filter(username="newuser").count() == 1
    response = context["response"]
    assert response.status_code == 302
    assert response.url == "/login/"
    context["response"] = client.get(response.url)


@then("the login page displays the registration success message")
def registration_success_message(context):
    content = context["response"].content.decode()
    assert "Your account has been created. You can now login" in content


@then("registration remains on the page and reports a duplicate username")
def duplicate_username_reported(context):
    response = context["response"]
    assert response.status_code == 200
    assert "users/register.html" in [
        template.name for template in response.templates
    ]
    assert "username" in response.context["form"].errors
    assert "A user with that username already exists." in response.content.decode()


@then("no additional user is created")
def no_additional_user():
    assert get_user_model().objects.count() == 1


@then("registration remains on the page and highlights the password2 field")
def password2_highlighted(context):
    response = context["response"]
    assert response.status_code == 200
    assert "users/register.html" in [
        template.name for template in response.templates
    ]
    assert "password2" in response.context["form"].errors
    assert "match" in str(response.context["form"].errors["password2"])


@then("no account is created")
def no_account_created():
    assert get_user_model().objects.count() == 0


@then("registration remains on the page and shows an email validation error")
def email_error_shown(context):
    response = context["response"]
    assert response.status_code == 200
    assert "users/register.html" in [
        template.name for template in response.templates
    ]
    assert "email" in response.context["form"].errors


# ---------------------------------------------------------------------------
# BDD-005 .. BDD-007: Authentication
# ---------------------------------------------------------------------------


@scenario("features/authentication.feature", "A registered user logs in")
def test_bdd_005_valid_login():
    pass


@scenario(
    "features/authentication.feature",
    "Login rejects incorrect credentials",
)
def test_bdd_006_invalid_login():
    pass


@scenario("features/authentication.feature", "An authenticated user logs out")
def test_bdd_007_logout():
    pass


@given('a registered user "alice" exists')
def registered_alice(context):
    context["user"] = make_user("alice")


@given('the registered user is on "/login/"')
def registered_user_on_login(client, context):
    context["response"] = client.get("/login/")
    assert context["response"].status_code == 200


@given('a user is on "/login/"')
def user_on_login(client, context):
    context["response"] = client.get("/login/")
    assert context["response"].status_code == 200


@when("the user enters the correct username and password and selects Login")
def submit_valid_login(client, context):
    context["response"] = client.post(
        "/login/",
        data={"username": "alice", "password": PASSWORD},
    )


@when(
    parsers.re(
        r'the user enters the username "(?P<username>[^"]*)" and password '
        r'"(?P<password>[^"]*)" and selects Login'
    )
)
def submit_login(client, context, username, password):
    context["response"] = client.post(
        "/login/",
        data={"username": username, "password": password},
    )


@then('the session is authenticated and the browser redirects to "/"')
def session_authenticated(client, context):
    response = context["response"]
    assert response.status_code == 302
    assert response.url == "/"
    assert client.session["_auth_user_id"] == str(context["user"].pk)


@then("authenticated navigation replaces Login/Register with Profile/Create Post/Logout")
def authenticated_navigation(client):
    content = client.get("/").content.decode()
    assert "Profile" in content
    assert "Create Post" in content
    assert "Logout" in content
    assert ">Login<" not in content
    assert ">Register<" not in content


@then("the login page remains visible and an authentication error is shown")
def login_error(context):
    response = context["response"]
    assert response.status_code == 200
    assert "users/login.html" in [
        template.name for template in response.templates
    ]
    assert "Please enter a correct username and password." in response.content.decode()


@then("no authenticated session is created")
def no_authenticated_session(client):
    assert "_auth_user_id" not in client.session


@given("the user is authenticated")
def user_is_authenticated(client, context):
    context["user"] = make_user("alice")
    client.force_login(context["user"])


@given("the user uses the Logout navigation link")
def user_uses_logout_link(context):
    context["logout_link"] = "/logout/"


@when("Django processes logout")
def django_processes_logout(client, context):
    context["response"] = client.get(context["logout_link"])


@then('the session is cleared and "/logout/" shows the logged-out message')
def session_cleared_and_message(client, context):
    response = context["response"]
    assert response.status_code == 200
    assert "users/logout.html" in [
        template.name for template in response.templates
    ]
    assert "You have been logged out !" in response.content.decode()
    assert "_auth_user_id" not in client.session


@then("Login/Register links replace the authenticated navigation links")
def anonymous_navigation(client):
    content = client.get("/").content.decode()
    assert ">Login<" in content
    assert ">Register<" in content
    assert ">Logout<" not in content


# ---------------------------------------------------------------------------
# BDD-008 .. BDD-011: Blog viewing
# ---------------------------------------------------------------------------


@scenario("features/blog_viewing.feature", "A public visitor views the blog listing")
def test_bdd_008_blog_listing():
    pass


@scenario("features/blog_viewing.feature", "Listing renders when no posts exist")
def test_bdd_009_empty_blog_listing():
    pass


@scenario("features/blog_viewing.feature", "A visitor opens an existing post")
def test_bdd_010_view_existing_post():
    pass


@scenario(
    "features/blog_viewing.feature",
    "Detail returns 404 for an unknown post",
)
def test_bdd_011_unknown_post():
    pass


@given("one or more posts exist")
def posts_exist(context):
    user = make_user("author")
    context["posts"] = [
        Post.objects.create(title="First Post", content="First content", author=user),
        Post.objects.create(title="Second Post", content="Second content", author=user),
    ]


@when('a public visitor opens "/"')
def public_visitor_opens_home(client, context):
    context["response"] = client.get("/")


@then("each post displays its title, content, author, and date")
def posts_displayed(context):
    response = context["response"]
    assert response.status_code == 200
    content = response.content.decode()
    for post in context["posts"]:
        assert post.title in content
        assert post.content in content
        assert post.author.username in content
        assert post.date_posted.strftime("%B %d, %Y") in content


@then("the visitor can click a title and open its detail page")
def title_opens_detail(client, context):
    post = context["posts"][0]
    response = client.get(f"/detail/{post.pk}/")
    assert response.status_code == 200
    assert post.title in response.content.decode()


@given("the database contains no posts")
def no_posts_exist():
    assert Post.objects.count() == 0


@when('a visitor opens "/"')
def visitor_opens_home(client, context):
    context["response"] = client.get("/")


@then("the shared page and navigation remain visible without post cards")
def shared_page_without_posts(context):
    response = context["response"]
    assert response.status_code == 200
    content = response.content.decode()
    assert "Our Sidebar" in content
    assert "Home" in content
    assert "About" in content
    assert "article-title" not in content


@then("the public page renders successfully")
def public_page_renders(context):
    assert context["response"].status_code == 200


@given("a post exists with a known ID")
def post_with_known_id(context):
    user = make_user("author")
    context["post"] = Post.objects.create(
        title="Known Post",
        content="Known content",
        author=user,
    )
    context["other_post"] = Post.objects.create(
        title="Other Post",
        content="Other content",
        author=user,
    )


@given("the visitor is on the home listing")
def visitor_on_home(client, context):
    context["response"] = client.get("/")
    assert context["response"].status_code == 200


@when("the visitor follows that post's title link")
def follow_title_link(client, context):
    context["response"] = client.get(f"/detail/{context['post'].pk}/")


@then("the detail page displays the matching title, content, author, and date")
def detail_displays_post(context):
    response = context["response"]
    assert response.status_code == 200
    content = response.content.decode()
    post = context["post"]
    assert post.title in content
    assert post.content in content
    assert post.author.username in content
    assert post.date_posted.strftime("%B %d, %Y") in content


@then("the detail page shows the selected post only")
def detail_shows_selected_post(context):
    content = context["response"].content.decode()
    assert context["other_post"].title not in content


@given("the requested post ID does not exist")
def requested_post_does_not_exist():
    assert not Post.objects.filter(pk=999999).exists()


@when("a visitor requests the detail page for an unknown ID")
def request_unknown_detail(client, context):
    context["response"] = client.get("/detail/999999/")


@then("the application returns an HTTP 404 response")
def response_is_404(context):
    assert context["response"].status_code == 404


@then("no nonexistent post data is rendered")
def no_post_data_rendered(context):
    assert "article-title" not in context["response"].content.decode()


# ---------------------------------------------------------------------------
# BDD-012 .. BDD-014: Blog creation
# ---------------------------------------------------------------------------


@scenario(
    "features/blog_creation.feature",
    "An authenticated user creates a valid post",
)
def test_bdd_012_create_valid_post():
    pass


@scenario(
    "features/blog_creation.feature",
    "Anonymous visitors cannot create posts",
)
def test_bdd_013_block_anonymous_post_creation():
    pass


@scenario(
    "features/blog_creation.feature",
    "Post creation rejects empty or overlong values",
)
def test_bdd_014_reject_invalid_post():
    pass


@given("the user is logged in")
def user_is_logged_in(client, context):
    context["user"] = make_user("alice")
    client.force_login(context["user"])


@given('the user is on "/create-post/"')
def user_on_create_post(client, context):
    context["response"] = client.get("/create-post/")
    assert context["response"].status_code == 200


@when("the user enters a valid title and content and selects Save")
def submit_valid_post(client, context):
    context["response"] = client.post(
        "/create-post/",
        data={"title": "BDD Post", "content": "BDD content"},
    )


@then('one post is created for the logged-in author and the browser redirects to "/"')
def post_created_and_redirected(context):
    response = context["response"]
    assert response.status_code == 302
    assert response.url == "/"
    assert Post.objects.count() == 1
    assert Post.objects.get().author == context["user"]


@then("the new post appears on the home listing and a success message is visible")
def post_visible_on_home(client):
    content = client.get("/").content.decode()
    assert "BDD Post" in content
    assert "The post has been created successfully." in content


@given("the visitor is not logged in")
def visitor_is_not_logged_in(client):
    assert "_auth_user_id" not in client.session


@when('the visitor requests "/create-post/"')
def visitor_requests_create_post(client, context):
    context["response"] = client.get("/create-post/")


@then("the visitor is redirected to login with a next parameter")
def redirected_to_login_with_next(context):
    response = context["response"]
    assert response.status_code == 302
    assert response.url == "/login/?next=/create-post/"


@then("no post is created and the protected page is not displayed")
def no_post_and_no_page(context):
    assert Post.objects.count() == 0
    assert context["response"].status_code == 302


@when(
    parsers.re(
        r'the user submits the title "(?P<title>.*)" and content '
        r'"(?P<content>.*)" and selects Save'
    )
)
def submit_post(client, context, title, content):
    context["response"] = client.post(
        "/create-post/",
        data={"title": title, "content": content},
    )


@then("the form remains on the page and shows the relevant validation errors")
def form_errors_shown(context):
    response = context["response"]
    assert response.status_code == 200
    assert "blog/create_post.html" in [
        template.name for template in response.templates
    ]
    errors = response.context["form"].errors
    assert "title" in errors or "content" in errors


@then("no invalid post is persisted")
def no_invalid_post():
    assert Post.objects.count() == 0


# ---------------------------------------------------------------------------
# BDD-015 .. BDD-016: Profile management
# ---------------------------------------------------------------------------


@scenario(
    "features/profile.feature",
    "An authenticated user views profile details",
)
def test_bdd_015_view_profile():
    pass


@scenario(
    "features/profile.feature",
    "Anonymous visitors cannot view profile",
)
def test_bdd_016_block_anonymous_profile():
    pass


@given("the user is logged in and has a profile created by the post-save signal")
def user_with_signal_profile(client, context):
    user = make_user("alice")
    assert Profile.objects.filter(user=user).count() == 1, (
        "users.signals.create_profile is not connected: no Profile was created "
        "for the new User"
    )
    context["user"] = user
    client.force_login(user)


@when('the user opens "/profile/"')
def user_opens_profile(client, context):
    context["response"] = client.get("/profile/")


@then("the profile image, username, and email are visible")
def profile_details_visible(context):
    response = context["response"]
    assert response.status_code == 200
    content = response.content.decode()
    assert context["user"].username in content
    assert context["user"].email in content
    assert "rounded-circle account-img" in content
    assert 'src=""' not in content


@then("the correct authenticated user's details are displayed")
def correct_profile_user(context):
    assert context["response"].context["user"] == context["user"]


@when('the visitor requests "/profile/"')
def visitor_requests_profile(client, context):
    context["response"] = client.get("/profile/")


@then("the visitor is redirected to login")
def visitor_redirected_to_login(context):
    response = context["response"]
    assert response.status_code == 302
    assert response.url == "/login/?next=/profile/"


@then("no profile is displayed")
def no_profile_displayed(context):
    assert context["response"].status_code == 302
