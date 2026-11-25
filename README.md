# Django Blog App

![Blog App Banner](https://i.imgur.com/oN71fj9.jpg)

### Demo 🎥

![BlogApp Demo](https://i.imgur.com/mpntklM.gif)

### Development 👨‍💻
**Note:** Use Python 3.12 for the recommended Windows setup.

### Windows Environment Setup 🚀

Open PowerShell in the project directory.

Create a virtual environment:

```powershell
py -3.12 -m venv venv
```

Activate the environment:

```powershell
.\venv\Scripts\Activate.ps1
```

If PowerShell blocks script execution, enable it for the current process:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\venv\Scripts\Activate.ps1
```

Install the project dependencies:

```powershell
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

Apply database migrations:

```powershell
python manage.py migrate
```

Create an administrator account:

```powershell
python manage.py createsuperuser
```

Enter your desired username, email and password. Make sure you remember them as you'll need them in future.

eg.

    Username: admin

    Email: admin@admin.com

    Password: HighlyConfidentialPassword

Start the Django development server:

```powershell
python manage.py runserver
```

Open http://127.0.0.1:8000/ in your browser.

To stop the server, press `Ctrl+C` in PowerShell.

To exit the virtual environment:

```powershell
deactivate
```

---

## Testing 🧪

All commands below assume the virtual environment is activated and the current
directory is the repository root.

### 1. Install the test dependencies

```powershell
python -m pip install -r requirements-test.txt
python -m playwright install chromium
```

`requirements-test.txt` installs Pytest, pytest-django, pytest-bdd,
pytest-playwright and allure-pytest. The second command downloads the Chromium
browser used by the Playwright UI tests; run `python -m playwright install`
instead if you want every supported browser.

### 2. Run the full test suite

```powershell
python -m pytest
```

No extra flags are required. The configuration in `pytest.ini` already enables:

- verbose progress with `PASSED`, `FAILED`, `SKIPPED` and `ERROR` statuses;
- short tracebacks with assertion details and expected/actual values;
- a short summary of failed, errored and skipped tests;
- the slowest ten test durations;
- total test count and total execution duration;
- automatic Allure result generation.

Pytest-django creates and destroys a separate test database automatically; the
development database (`db.sqlite3`) is not modified.

### 3. Run a subset of the tests

```powershell
# UI (Playwright) tests
python -m pytest tests/ui

# BDD (pytest-bdd) tests
python -m pytest tests/bdd

# By marker
python -m pytest -m ui
python -m pytest -m bdd

# A single test
python -m pytest "tests/ui/test_ui.py::test_ui_001_home_listing_shows_posts_and_opens_detail"

# Tests whose name matches a keyword
python -m pytest -k login

# List tests without executing them
python -m pytest --collect-only
```

### 4. Run UI tests in a visible browser

```powershell
python -m pytest tests/ui --headed
```

Choose another engine (install it first, e.g.
`python -m playwright install firefox`):

```powershell
python -m pytest tests/ui --browser firefox
```

### 5. Read the results

Terminal statuses:

| Status | Meaning |
|---|---|
| `PASSED` | The test completed and all assertions matched. |
| `FAILED` | An assertion executed, but the actual result did not match the expected result. |
| `ERROR` | The test could not run because of a fixture, browser, database or teardown problem. |
| `SKIPPED` | The test was deliberately skipped. |

Pytest prints a concise summary of every failed, errored and skipped test,
including the test name and location, followed by the total counts and session
duration.

Diagnostic files produced by a run:

- `reports/pytest.log` – per-run log with one status line per test.
- `allure-results/` – Allure result files, regenerated on every run. Failures in
  UI tests include a screenshot, the page URL/title and captured logs.

### 6. View the Allure report

Pytest writes `allure-results/` automatically. To render it, install the
[Allure command-line tool](https://allurereport.org/docs/install/) and make sure
`allure` is on `PATH`:

```powershell
allure serve allure-results
```

Or build and open a static report:

```powershell
allure generate allure-results -o allure-report --clean
allure open allure-report
```

`allure-results/`, `allure-report/` and `reports/` are generated folders and are
ignored by Git.

### 7. Useful execution options

```powershell
# Show local variables in tracebacks when debugging a failure
python -m pytest --showlocals

# Re-run only the tests that failed during the previous run
python -m pytest --lf
```

Avoid `-x` / `--maxfail=1` for normal runs: by default Pytest continues after a
failure, so one failing test does not prevent the remaining tests from running.

---

## Running UI Tests in Chrome (Visible Browser)

The UI tests use Playwright, and the current project configuration uses
Playwright's Chromium browser by default. No `--browser` flag is required.
Chromium is the open-source browser that Playwright installs and drives for
Chrome/Chromium testing.

The `--headed` flag is the command-line option that tells Playwright to open a
visible Chromium browser window while the tests execute. Without `--headed`,
Playwright runs in headless mode.

All commands below assume the virtual environment is activated and the current
directory is the repository root. The Django application is started
automatically by pytest-django's `live_server` fixture, so you do not need to run
`python manage.py runserver` separately.

### Run all UI tests with Chrome visible

```powershell
python -m pytest -m ui --headed -v
```

### Run a specific UI test with Chrome visible

```powershell
python -m pytest tests/ui/test_ui.py::test_ui_001_home_listing_shows_posts_and_opens_detail --headed -v
```

### Run UI tests in headless mode

```powershell
python -m pytest -m ui -v
```

### Headed vs headless mode

- **Headed mode (`--headed`):** opens a visible Chromium browser window while the
  tests execute, so the interactions can be observed as they happen.
- **Headless mode:** executes the browser tests in the background without
  displaying a browser window.

### Troubleshooting

If Playwright reports that Chromium is not installed, download the browser
binary and then re-run the desired command:

```powershell
python -m playwright install chromium
```
