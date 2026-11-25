# Django Blog Application Testing Documentation

## 1. Testing Objective and Scope

This document is a testing blueprint for the existing Django Blog Application. It describes planned isolated unit tests, browser UI tests, and behavior scenarios based on the source code that is present. It does not propose application changes or define executable test code.

The application has blog listing/detail/about screens, registration, login, logout, profile display, and authenticated post creation. It does not contain routes or templates for editing or deleting posts, editing a profile, password reset, or search/filtering.

## Table of Contents

1. [Testing Objective and Scope](#1-testing-objective-and-scope)
2. [Technology Stack](#2-technology-stack)
3. [Pytest Testing Plan](#3-pytest-testing-plan)
4. [Playwright UI Testing Plan](#4-playwright-ui-testing-plan)
5. [Gherkin BDD Scenario Plan](#5-gherkin-bdd-scenario-documentation)
6. [Testing Coverage Matrix](#6-testing-coverage-matrix)
7. [Testing Boundaries](#7-testing-boundaries)
8. [Test Case Summary](#8-test-case-summary)

## 2. Technology Stack

### 2.1 Application Technology Stack

| Category | Technology | Version | Purpose |
|---|---|---:|---|
| Frontend | HTML5 templates | Not Specified | Renders server-side pages in Django templates |
| Frontend | CSS | Not Specified | Styles the application through `django_project/static/blog/main.css` |
| Frontend | JavaScript | Not Specified | Provides Bootstrap navbar and responsive components |
| Frontend | Bootstrap | 4.0.0 | Provides navbar, grid, form, alert, and responsive styling |
| Frontend | jQuery | 3.2.1.slim | Supports Bootstrap 4 JavaScript behavior |
| Frontend | Popper.js | 1.12.9 | Provides positioning support for Bootstrap components |
| Backend | Django | 4.2.10 | Provides routing, views, templates, authentication, ORM, and forms |
| Database | SQLite | 3 through Django, exact library version Not Specified | Stores application data in `db.sqlite3` |
| Programming Language | Python | 3.10.6 | Declared runtime in `runtime.txt` |
| Frameworks | Django | 4.2.10 | Server-side application framework |
| Libraries | django-crispy-forms | 2.0 | Renders Django forms using template packs |
| Libraries | crispy-bootstrap5 | 0.7 | Supplies the Bootstrap 5 template pack used by Crispy Forms |
| Libraries | Pillow | 10.2.0 | Supports `ImageField` profile image handling |
| Libraries | Gunicorn | 20.1.0 | WSGI server dependency |
| Libraries | WhiteNoise | 6.4.0 | Static-file middleware dependency |
| Other Tools | Django migrations | Django 4.2.10 | Defines and applies database schema changes |
| Other Tools | Django development server | Django 4.2.10 | Runs the application locally |
| Other Tools | Gunicorn | 20.1.0 | Provides a deployment WSGI server |
| Other Tools | WhiteNoise | 6.4.0 | Supports static-file deployment |
| Other Tools | Bash build script | Not Specified | Installs dependencies, collects static files, and runs migrations |

The repository also contains Bootstrap's CSS and JavaScript loaded from CDN URLs. The application source does not contain a separate React, Angular, Vue, or Node.js frontend.

### 2.2 Testing Technology Stack

| Technology | Purpose | Planned Usage |
|---|---|---|
| Python | Test programming language | Writing later Pytest and pytest-bdd test code compatible with the Django application |
| Pytest | Test execution framework | Executing isolated Django model, form, signal, and view tests |
| Playwright | Browser automation | Testing browser screens, controls, navigation, validation, and responsive behavior |
| Gherkin | BDD scenario language | Describing human-readable Given-When-Then application behavior |
| pytest-bdd | BDD integration | Connecting Gherkin scenarios to Pytest step implementations later |

Pytest, Playwright, and pytest-bdd versions are **Not Specified** because no testing dependency file or testing configuration remains in the cleaned repository.

### 2.3 Technology Stack Explanation

#### Application technologies

- **Python** is the application language. `runtime.txt` declares Python 3.10.6. The `README.md` recommends Python 3.12 for Windows setup, but 3.12 is setup guidance rather than a repository runtime declaration.
- **Django 4.2.10** implements models, URL routing, views, templates, authentication, ORM behavior, forms, messages, migrations, and static/media configuration.
- **HTML5, CSS, and JavaScript** provide server-rendered UI content. Django templates are stored in `blog/templates/` and `users/templates/`.
- **Bootstrap 4.0.0** supplies the navigation, layout, and form styling declared in `blog/templates/blog/base.html`. jQuery 3.2.1.slim and Popper.js 1.12.9 support Bootstrap behavior.
- **SQLite** is configured in `django_project/settings.py` and stores the local database in `db.sqlite3`.
- **django-crispy-forms 2.0** and **crispy-bootstrap5 0.7** render registration and login fields with Bootstrap 5-compatible markup.
- **Pillow 10.2.0** supports the `Profile.image` `ImageField`.
- **Gunicorn 20.1.0** is the declared WSGI deployment server.
- **WhiteNoise 6.4.0** is a declared static-file dependency; its middleware is not currently enabled in `django_project/settings.py`.
- **Django migrations** maintain the existing `Post`, `Profile`, and related database schemas.
- **The Bash build script** defines deployment steps for dependency installation, static collection, and migrations.

#### Testing technologies

- **Pytest** will execute isolated test functions against the Django settings, database, forms, models, signals, and test client.
- **Playwright** will drive a real browser against the running Django development server and inspect visible UI behavior.
- **Gherkin** will provide human-readable acceptance specifications for workflows already implemented in the repository.
- **pytest-bdd** would act as a bridge between Gherkin feature behavior and later Pytest step functions. No `.feature` file or pytest-bdd integration is included now.
- **Python** remains the shared programming language between application code and planned Pytest/pytest-bdd implementation.

#### Dependency status

The application dependencies already identified in `requirements.txt` are:

- Django 4.2.10
- django-crispy-forms 2.0
- Pillow 10.2.0
- crispy-bootstrap5 0.7
- Gunicorn 20.1.0
- WhiteNoise 6.4.0

No testing dependencies are currently declared in the repository. Pytest, Playwright, pytest-bdd, and browser binaries are therefore expected to require installation and version decisions later. This document does not perform or assume an installation.

## 3. Pytest Testing Plan

Pytest will test isolated Django behavior and application logic. Django test client requests may be used where the behavior under test is a view's returned response or database side effect. Browser rendering, visible controls, and client navigation belong to Playwright.

### 3.1 Model and Signal Behavior

| Test ID | Module/file | Function or method | Purpose | Preconditions and input/test data | Testing objective and expected result | Positive cases | Negative cases | Boundary cases |
|---|---|---|---|---|---|---|---|---|
| PY-001 | `blog/models.py` | `Post.__str__` | Returns the post title as a readable representation | A saved post exists; title is `"Test Post"` | Verify readable representation | Exact title is returned | No valid negative input; `None` is not valid model data | `None` |
| PY-002 | `blog/models.py` | `Post.__str__` | Returns the title at the model's maximum declared length | A post with title `"T" * 100` | Verify complete title is returned | Exact 100-character title | A 101-character value is not valid model-method input and should be rejected by the form | Exactly 100 characters |
| PY-003 | `blog/models.py` | `Post.author` cascade behavior | Enforces the foreign-key relationship to `User` | One user and at least one post by that user | Deleting the author deletes its posts | User with no posts remains valid | Author deletion removes every associated post | `None` |
| PY-004 | `users/models.py` | `Profile.__str__` | Returns a readable profile name | A user named `alice` has a profile | Verify the profile string | `alice Profile` is returned | No valid negative input | `None` |
| PY-005 | `users/signals.py` | `create_profile` | Creates a profile automatically after a new `User` is created | Call post-save with `created=True` | Exactly one profile is created | Newly created user | Saving existing user must not create another profile | `None` |
| PY-006 | `users/signals.py` | `create_profile` | Avoids duplicate profile creation on repeated saves | An existing user and profile; call post-save with `created=False` | Profile count remains one | `None` | Saving existing user creates no second profile | `None` |

### 3.2 Form Validation

| Test ID | Module/file | Function or method | Purpose | Preconditions and input/test data | Testing objective and expected result | Positive cases | Negative cases | Boundary cases |
|---|---|---|---|---|---|---|---|---|
| PY-007 | `blog/forms.py` | `PostForm` inherited `is_valid()` and `clean()` | Validates title and content | No database record exists; title `"Valid post"`; content `"Valid content"` | Form is valid and exposes only `title` and `content` | Normal title and content | Empty title or content | Exactly 100-character title |
| PY-008 | `blog/forms.py` | `PostForm` inherited field validation | Rejects a missing title | Empty or omitted title; content `"Content"` | Form is invalid with a title-related error | `None` | Empty title | Minimum valid length is 1 character |
| PY-009 | `blog/forms.py` | `PostForm` inherited field validation | Rejects missing content | Valid title; empty or omitted content | Form is invalid with a content-related error | `None` | Empty content | Minimum valid length is 1 character |
| PY-010 | `blog/forms.py` | `PostForm` inherited `MaxLengthValidator` | Verifies title length limit | No database record; title `"T" * 100`; content `"Content"` | Form is valid | 100 characters | 101-character title | Exactly 100 characters |
| PY-011 | `blog/forms.py` | `PostForm` inherited `MaxLengthValidator` | Rejects title over the limit | No database record; title `"T" * 101`; content `"Content"` | Form is invalid with a title length error | `None` | 101 characters | 100 passes; 101 fails |
| PY-012 | `users/forms.py` | `UserRegisterForm` inherited validation | Validates registration data | No existing account; unique username; valid email; matching strong passwords | Form is valid and saves a `User` | Valid complete data | Duplicate username, mismatch, invalid email, weak password | Django username/password limits |
| PY-013 | `users/forms.py` | `UserRegisterForm.clean_username` inherited behavior | Rejects an existing username | A user named `existing` is present | Form is invalid with a username error | `None` | Duplicate username `existing` | `None` |
| PY-014 | `users/forms.py` | `UserRegisterForm.clean_password2` inherited behavior | Rejects mismatched passwords | Valid username/email; password1 differs from password2 | Form is invalid with a password2 error | Matching passwords | Mismatched passwords | `None` |
| PY-015 | `users/forms.py` | `UserRegisterForm.clean_email` inherited behavior | Validates required email format | Valid username/password; email is empty or malformed | Form is invalid with an email error | `name@example.com` | Empty or malformed email | `None` |
| PY-016 | `users/forms.py` | Django `UserCreationForm` inherited password validation | Rejects weak passwords | Valid username/email; test password variants | Form is invalid with password-related errors | Strong password | Too short or username-related password | 8-character minimum |

### 3.3 View and Business Logic Behavior

| Test ID | Module/file | Function or method | Purpose | Preconditions and input/test data | Testing objective and expected result | Positive cases | Negative cases | Boundary cases |
|---|---|---|---|---|---|---|---|---|
| PY-017 | `blog/views.py` | `home` | Supplies all posts to public listing | Public GET; database empty or populated | HTTP 200, `blog/home.html`, and correct post context | Populated database | Empty database still renders | `None` |
| PY-018 | `blog/views.py` | `about` | Renders the About page | Public GET | HTTP 200 and title `"About"` | Normal GET | `None` | `None` |
| PY-019 | `blog/views.py` | `post_detail` | Retrieves one post or reports it missing | Existing ID and unknown ID | Existing post renders; unknown ID returns 404 | Existing integer ID | Unknown integer ID | Integer ID limits are not source-defined |
| PY-020 | `blog/views.py` | `create_post` | Blocks anonymous users | No authenticated session; GET or POST | Redirect to login with `next=/create-post/` | `None` | Anonymous GET and POST | `None` |
| PY-021 | `blog/views.py` | `create_post` | Renders an empty form for auth user | Authenticated GET | HTTP 200, `blog/create_post.html`, and `PostForm` | Authenticated user | Anonymous redirect | `None` |
| PY-022 | `blog/views.py` | `create_post` | Creates and assigns a post | Authenticated POST; valid title and content | One post saved to current user, success message, redirect home | Complete valid data | Unauthenticated POST | `None` |
| PY-023 | `blog/views.py` | `create_post` | Prevents invalid title persistence | Authenticated POST; empty or 101-character title | HTTP 200, re-rendered form, no post saved | `None` | Empty and 101-character title | 100-character title passes |
| PY-024 | `blog/views.py` | `create_post` | Prevents invalid content persistence | Authenticated POST; valid title and empty content | HTTP 200, re-rendered form, no post saved | `None` | Empty content | `None` |
| PY-025 | `users/views.py` | `register` | Renders registration form | Public GET | HTTP 200, `users/register.html`, and `UserRegisterForm` | Anonymous GET | `None` | `None` |
| PY-026 | `users/views.py` | `register` | Creates a user | Public POST with valid complete data | User saved, success message, redirect login | Valid registration | Duplicate, mismatch, invalid email | `None` |
| PY-027 | `users/views.py` | `register` | Prevents duplicate registration | An existing username and matching duplicate POST | Existing record remains only match; HTTP 200 | `None` | Reused username | `None` |
| PY-028 | `django_project.urls` Django login view | Login authentication | Allows valid login | Existing user; correct username/password | Redirect home and authenticated session | Correct credentials | Wrong password or unknown user | `None` |
| PY-029 | `django_project.urls` Django login view | Rejects invalid authentication | Existing user or unknown user; incorrect credentials | HTTP 200 login page and no session | `None` | Wrong password or unknown user | `None` |
| PY-030 | `django_project.urls` Django logout view | Ends authenticated session | Authenticated POST logout | Redirect and session cleared | Authenticated logout | Anonymous behavior is Django-dependent | `None` |
| PY-031 | `users/views.py` | `profile` | Blocks anonymous access | No authenticated session; GET `/profile/` | Redirect to login | `None` | Anonymous GET | `None` |
| PY-032 | `users/views.py` | `profile` | Displays authenticated profile | Authenticated user with associated profile | HTTP 200, `users/profile.html`, correct user image/name/email | Existing profile | Missing profile is a defect candidate | `None` |

The following source functions are not suitable for isolated Pytest:

- `manage.py:main()` is a Django process entry point rather than application business logic.
- `blog.views.home`, `blog.views.about`, and `blog.views.post_detail` contain request/render behavior; their HTTP and context behavior is tested through Django test-client requests, while visible layout is reserved for Playwright.
- `blog.views.create_post`, `users.views.register`, `profile`, Django login/logout views are request workflows and database side effects. They are suitable for Django test-client tests, not pure unit tests.
- `PostForm.Meta` and `UserRegisterForm.Meta` are declarative configuration, not callable application behavior. Their effects are covered through form validation tests.

## 4. Playwright UI Testing Plan

Playwright will test only browser-visible behavior: navigation, forms, controls, validation messages, page state, and responsive layout. It will not test database internals or API responses directly.

| Screen ID | Screen/page name | URL or route | Purpose | UI elements to test | User interactions to verify | Expected UI behavior | Validation behavior | Navigation behavior | Positive and negative test cases |
|---|---|---|---|---|---|---|---|---|---|
| UI-001 | Home/blog listing | `/` (`blog-home`) | Shows all posts publicly | Navbar, post cards, author, date, title, content, sidebar, mobile navbar toggle | Open page; click post title; toggle mobile navbar | Visible posts and shared layout | No form validation | Public access; title opens detail route | Positive: populated database. Negative: empty database. |
| UI-002 | Home empty state | `/` (`blog-home`) | Confirms public listing with no posts | Shared navbar and sidebar | Open page; inspect content | Page loads without post cards | `None` | Navigation links remain usable | Negative: no posts in database |
| UI-003 | About | `/about/` (`blog-about`) | Displays static About content | Heading and navbar | Open and navigate from navbar | `"About Page !"` heading is visible | `None` | Returns to home and other navbar destinations | Positive: direct and navbar navigation |
| UI-004 | Registration | `/register/` (`register`) | Creates a user account | Username, email, password1, password2, Sign Up button, Sign In link | Enter fields; submit valid/invalid data | Form renders and success redirects to login | Inline duplicate, mismatch, email, and password errors | Sign In link opens login; success opens login | Positive: valid registration; Negative: duplicate, mismatch, malformed email |
| UI-005 | Login | `/login/` (`login`) | Authenticates a user | Username, password, Login button, Sign Up link | Enter credentials; submit | Navbar changes to authenticated state after success | Django login error for invalid credentials | Success redirects to `/`; Sign Up opens register | Positive: valid credentials; Negative: wrong password and unknown user |
| UI-006 | Logout | `/logout/` (`logout`) | Ends the logged-in session | Logout link, logged-out heading, Login Again link | Sign out and open result | `"You have been logged out !"`, login prompt | `None` | Login Again opens login | Positive: authenticated logout |
| UI-007 | Blog detail | `/detail/<id>/` (`detail`) | Displays one post | Title, content, author, date, author image area | Open from home; inspect detail | Selected post's complete data is visible | `None` | Missing ID should show 404 page; home link remains | Positive: existing ID; Negative: unknown ID |
| UI-008 | Create post | `/create-post/` (`create_post`) | Creates a post as the logged-in user | Title input, content textarea, Save button | Submit valid and invalid values | Valid data creates post and redirects to home with success message | Empty required fields and title over 100 characters show errors | Anonymous access redirects to login | Positive: valid creation; Negative: empty fields, 101-character title; Anonymous: redirect |
| UI-009 | Profile | `/profile/` (`profile`) | Displays the authenticated user's profile | Circular image, username, email | Open after login; inspect values | Image, username, and email are visible | `None` | Anonymous access redirects to login | Positive: authenticated user; Negative: anonymous user |
| UI-010 | Shared responsive navigation | Visible across all routes | Verifies layout and navigation state | Desktop navbar links, mobile toggle, collapsed menu | Resize viewport; toggle menu; click links | Logged-out and logged-in link sets update correctly | `None` | Home, About, Profile, Create Post, Logout/Login/Register links work according to auth state | Positive: desktop/mobile and authenticated/anonymous states |

The following requested UI areas are not implemented and cannot be verified: edit post, delete post confirmation, profile editing and image upload, password reset pages, and search/filter controls. Django `Profile.image` exists and profile templates display `user.profile.image`, but no upload form or upload route exists, so image upload is unverified.

## 5. Gherkin BDD Scenario Documentation

These scenarios describe behavior only and do not imply implementation of `.feature` files.

### BDD-001: Register a new user

- **Feature/module:** User registration
- **Scenario title:** A visitor registers with valid details
- **Scenario type:** Positive
- **Preconditions:** The username and email are not already used.
- **Given:** The visitor is on `/register/`.
- **When:** The visitor enters a unique username, a valid email, and matching strong passwords, then selects Sign Up.
- **Then:** A user account is created and the visitor is redirected to `/login/`.
- **Expected outcome:** One new user exists and the login page is displayed with the success message.

### BDD-002: Reject duplicate username

- **Feature/module:** User registration
- **Scenario title:** Registration rejects an existing username
- **Scenario type:** Negative
- **Preconditions:** A user with the selected username already exists.
- **Given:** A visitor is on `/register/`.
- **When:** The visitor submits the existing username with otherwise valid data.
- **Then:** Registration remains on the page and reports a duplicate username.
- **Expected outcome:** No additional user is created.

### BDD-003: Reject mismatched passwords

- **Feature/module:** User registration
- **Scenario title:** Registration rejects password mismatch
- **Scenario type:** Negative
- **Preconditions:** No account has been created for the submitted username.
- **Given:** A visitor is on `/register/`.
- **When:** The visitor enters two different passwords and submits.
- **Then:** Registration remains on the page and highlights the password2 field.
- **Expected outcome:** No account is created.

### BDD-004: Reject invalid email

- **Feature/module:** User registration
- **Scenario title:** Registration validates email format
- **Scenario type:** Negative
- **Preconditions:** The other registration fields are valid.
- **Given:** A visitor is on `/register/`.
- **When:** The visitor submits an empty or malformed email.
- **Then:** Registration remains on the page and shows an email validation error.
- **Expected outcome:** No account is created.

### BDD-005: Log in with valid credentials

- **Feature/module:** Authentication
- **Scenario title:** A registered user logs in
- **Scenario type:** Positive
- **Preconditions:** A user account exists.
- **Given:** The registered user is on `/login/`.
- **When:** The user enters the correct username and password and selects Login.
- **Then:** The session is authenticated and the browser redirects to `/`.
- **Expected outcome:** Authenticated navigation replaces Login/Register with Profile/Create Post/Logout.

### BDD-006: Reject invalid login

- **Feature/module:** Authentication
- **Scenario title:** Login rejects incorrect credentials
- **Scenario type:** Negative
- **Preconditions:** A user account exists.
- **Given:** A user is on `/login/`.
- **When:** The user enters an unknown username or incorrect password and selects Login.
- **Then:** The login page remains visible and an authentication error is shown.
- **Expected outcome:** No authenticated session is created.

### BDD-007: Log out

- **Feature/module:** Authentication
- **Scenario title:** An authenticated user logs out
- **Scenario type:** Positive
- **Preconditions:** The user is authenticated.
- **Given:** The user uses the Logout navigation link.
- **When:** Django processes logout.
- **Then:** The session is cleared and `/logout/` shows the logged-out message.
- **Expected outcome:** Login/Register links replace the authenticated navigation links.

### BDD-008: View blog listing

- **Feature/module:** Blog viewing
- **Scenario title:** A public visitor views the blog listing
- **Scenario type:** Positive
- **Preconditions:** One or more posts exist.
- **Given:** A public visitor opens `/`.
- **When:** The page loads.
- **Then:** Each post displays its title, content, author, and date.
- **Expected outcome:** The visitor can click a title and open its detail page.

### BDD-009: View empty blog listing

- **Feature/module:** Blog viewing
- **Scenario title:** Listing renders when no posts exist
- **Scenario type:** Boundary
- **Preconditions:** The database contains no posts.
- **Given:** A visitor opens `/`.
- **When:** The listing view queries posts.
- **Then:** The shared page and navigation remain visible without post cards.
- **Expected outcome:** The public page renders successfully.

### BDD-010: View an existing post

- **Feature/module:** Blog viewing
- **Scenario title:** A visitor opens an existing post
- **Scenario type:** Positive
- **Preconditions:** A post exists with a known ID.
- **Given:** The visitor is on the home listing.
- **When:** The visitor follows that post's title link.
- **Then:** `/detail/<id>/` displays the matching title, content, author, and date.
- **Expected outcome:** The detail page shows the selected post only.

### BDD-011: Missing post detail

- **Feature/module:** Blog viewing
- **Scenario title:** Detail returns 404 for an unknown post
- **Scenario type:** Negative
- **Preconditions:** The requested post ID does not exist.
- **Given:** A visitor requests `/detail/<unknown-id>/`.
- **When:** The detail view executes.
- **Then:** The application returns an HTTP 404 response.
- **Expected outcome:** No nonexistent post data is rendered.

### BDD-012: Create a blog post

- **Feature/module:** Blog creation
- **Scenario title:** An authenticated user creates a valid post
- **Scenario type:** Positive
- **Preconditions:** The user is logged in.
- **Given:** The user is on `/create-post/`.
- **When:** The user enters a valid title and content and selects Save.
- **Then:** One post is created for the logged-in author and the browser redirects to `/`.
- **Expected outcome:** The new post appears on the home listing and a success message is visible.

### BDD-013: Block anonymous post creation

- **Feature/module:** Blog creation
- **Scenario title:** Anonymous visitors cannot create posts
- **Scenario type:** Negative
- **Preconditions:** The visitor is not logged in.
- **Given:** The visitor requests `/create-post/`.
- **When:** Django evaluates the login decorator.
- **Then:** The visitor is redirected to login with a `next` parameter.
- **Expected outcome:** No post is created and the protected page is not displayed.

### BDD-014: Reject invalid blog post

- **Feature/module:** Blog creation
- **Scenario title:** Post creation rejects empty or overlong values
- **Scenario type:** Negative
- **Preconditions:** The user is authenticated.
- **Given:** The user is on `/create-post/`.
- **When:** The user submits an empty title, empty content, or a title longer than 100 characters.
- **Then:** The form remains on the page and shows the relevant validation errors.
- **Expected outcome:** No invalid post is persisted.

### BDD-015: View profile

- **Feature/module:** Profile management
- **Scenario title:** An authenticated user views profile details
- **Scenario type:** Positive
- **Preconditions:** The user is logged in and has a profile created by the post-save signal.
- **Given:** The user opens `/profile/`.
- **When:** The profile view renders.
- **Then:** The profile image, username, and email are visible.
- **Expected outcome:** The correct authenticated user's details are displayed.

### BDD-016: Block anonymous profile access

- **Feature/module:** Profile management
- **Scenario title:** Anonymous visitors cannot view profile
- **Scenario type:** Negative
- **Preconditions:** The visitor is not logged in.
- **Given:** The visitor requests `/profile/`.
- **When:** Django evaluates the login decorator.
- **Then:** The visitor is redirected to login.
- **Expected outcome:** No profile is displayed.

The following Gherkin workflows cannot be documented as executable application behavior because the source has no implementation: post editing, post deletion, profile editing, image upload, password reset, and search/filtering. Profile image display is present, but image upload is not.

## 6. Testing Coverage Matrix

| Application module | Relevant Python functions | Relevant UI screens | Gherkin scenarios | Testing technology |
|---|---|---|---|---|
| Blog model | `Post.__str__`, `Post.author` cascade behavior | Home, detail | BDD-008 through BDD-011 | Pytest; Playwright; Gherkin |
| Blog forms | `PostForm` validation | Create post | BDD-012 through BDD-014 | Pytest; Playwright; Gherkin |
| Blog views | `home`, `about`, `post_detail`, `create_post` | Home, About, detail, create post | BDD-008 through BDD-014 | Pytest; Playwright; Gherkin |
| User model/signals | `Profile.__str__`, `create_profile` | Profile | BDD-015 and BDD-016 | Pytest; Playwright; Gherkin |
| Registration form | `UserRegisterForm` inherited validation | Registration | BDD-001 through BDD-004 | Pytest; Playwright; Gherkin |
| Registration view | `register` | Registration | BDD-001 through BDD-004 | Pytest; Playwright; Gherkin |
| Authentication | Django LoginView and LogoutView | Login, Logout, shared navigation | BDD-005 through BDD-007 | Pytest; Playwright; Gherkin |
| Profile view | `profile` | Profile | BDD-015 and BDD-016 | Pytest; Playwright; Gherkin |
| URL routing | Django URL configuration | Shared navigation and all implemented screens | Scenarios that navigate between screens | Playwright; Gherkin; route checks may use Pytest if implemented later |

## 7. Testing Boundaries

### 7.1 Responsibilities

- **Pytest:** Tests Python and Django behavior without a browser. This includes model string and relationship behavior, form validation, signal behavior, view responses and context, authentication side effects, redirects, and database persistence.
- **Playwright:** Tests the browser-visible application. This includes controls, form submission, validation messages, navigation, visible state changes, logout/login state, and responsive layout.
- **Gherkin:** Describes end-user behavior in Given-When-Then language. Scenarios act as readable acceptance criteria and may later guide implementation of automated Playwright or Django tests.

### 7.2 Overlap and Complement

- Registration, login/logout, post creation, and profile access are covered at all three levels. Pytest verifies server behavior; Playwright verifies visible behavior; Gherkin defines the end-to-end expectation.
- Model, signal, and form validation tests belong primarily to Pytest.
- Buttons, input fields, messages, navigation, and responsive layout belong primarily to Playwright.
- Gherkin may repeat a workflow for acceptance clarity but should not duplicate lower-level implementation assertions.

### 7.3 Explicit exclusions

- API testing is excluded because no application API endpoints were found.
- Direct database schema testing is excluded except for behavior that the application itself exposes.
- Edit/delete post, profile editing, password reset, search/filtering, and image upload are excluded from the test plan because no source routes, views, or upload forms implement them.

## 8. Test Case Summary

### 8.1 Pytest Summary

| Module | Documented test IDs | Number of test cases |
|---|---|---:|
| Blog models | PY-001, PY-002, PY-003 | 3 |
| User models and signals | PY-004, PY-005, PY-006 | 3 |
| Blog form | PY-007, PY-008, PY-009, PY-010, PY-011 | 5 |
| User registration form | PY-012, PY-013, PY-014, PY-015, PY-016 | 5 |
| Blog views | PY-017, PY-018, PY-019, PY-020, PY-021, PY-022, PY-023, PY-024 | 8 |
| User and authentication views | PY-025, PY-026, PY-027, PY-028, PY-029, PY-030, PY-031, PY-032 | 8 |
| **Pytest total** | **PY-001 through PY-032** | **32** |

**Pytest variant distribution**

- **Positive test cases:** 16 test IDs contain an explicitly documented positive result: PY-001, PY-004, PY-005, PY-007, PY-010, PY-012, PY-017, PY-018, PY-019, PY-021, PY-022, PY-025, PY-026, PY-028, PY-030, and PY-032.
- **Negative test cases:** 14 test IDs contain an explicitly documented negative result: PY-003, PY-006, PY-008, PY-009, PY-013, PY-014, PY-015, PY-019, PY-020, PY-023, PY-024, PY-027, PY-029, and PY-031.
- **Boundary test cases:** 5 test IDs contain an explicitly documented boundary: PY-002, PY-010, PY-011, PY-016, and PY-023.

These are coverage categories, so PY-010 is counted as both positive and boundary and PY-019 is counted as both positive and negative. The 32 test IDs are not duplicated.

### 8.2 Playwright Summary

| Screen/module | Documented test IDs | Number of test cases |
|---|---|---:|
| Home listing | UI-001, UI-002 | 2 |
| About | UI-003 | 1 |
| Registration | UI-004 | 1 |
| Login | UI-005 | 1 |
| Logout | UI-006 | 1 |
| Blog detail | UI-007 | 1 |
| Create post | UI-008 | 1 |
| Profile | UI-009 | 1 |
| Shared responsive navigation | UI-010 | 1 |
| **Playwright total** | **UI-001 through UI-010** | **10** |

The UI table's individual rows combine positive and negative variants for the same screen. If implemented later, each positive or negative variant should receive a separate Playwright test without changing the screen-level planned coverage IDs.

**Playwright variant distribution**

- **Positive coverage:** 9 screen test IDs document a successful interaction or visible state: UI-001, UI-003, UI-004, UI-005, UI-006, UI-007, UI-008, UI-009, and UI-010.
- **Negative coverage:** 7 screen test IDs document unsuccessful or unauthorized behavior: UI-001, UI-002, UI-004, UI-005, UI-007, UI-008, and UI-009.
- **Boundary coverage:** 2 screen test IDs document boundary behavior: UI-002 (empty database) and UI-008 (100/101-character title).

These categories overlap because one screen-level UI test ID may include both positive and negative browser behavior.

### 8.3 Gherkin Summary

| Feature/module | Documented scenario IDs | Number of scenarios |
|---|---|---:|
| Registration | BDD-001, BDD-002, BDD-003, BDD-004 | 4 |
| Authentication | BDD-005, BDD-006, BDD-007 | 3 |
| Blog viewing | BDD-008, BDD-009, BDD-010, BDD-011 | 4 |
| Blog creation | BDD-012, BDD-013, BDD-014 | 3 |
| Profile | BDD-015, BDD-016 | 2 |
| **Gherkin total** | **BDD-001 through BDD-016** | **16** |

**Gherkin scenario-type distribution**

- **Positive:** 7 scenarios: BDD-001, BDD-005, BDD-007, BDD-008, BDD-010, BDD-012, and BDD-015.
- **Negative:** 8 scenarios: BDD-002, BDD-003, BDD-004, BDD-006, BDD-011, BDD-013, BDD-014, and BDD-016.
- **Boundary:** 1 scenario: BDD-009.
