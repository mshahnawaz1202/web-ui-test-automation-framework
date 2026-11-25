"""Framework-wide pytest configuration, reporting and diagnostics.

This module contains execution infrastructure only.  It does not define,
modify, skip or otherwise influence test cases, and it never converts a
failing or erroring test into a successful one.

Responsibilities:

* readable terminal headers (environment and artifact locations);
* a per-run diagnostic log file under ``reports/``;
* Allure environment/category metadata;
* failure diagnostics in Allure (screenshot, page state, captured logs).

Pytest itself remains responsible for PASSED / FAILED / SKIPPED / ERROR
reporting and for the terminal summary, so no duplicate summary is printed
here.
"""

from __future__ import annotations

import json
import logging
import os
import platform
from importlib import metadata
from pathlib import Path

import pytest

try:  # Allure is a declared test dependency; stay import-safe regardless.
    import allure
    from allure_commons.types import AttachmentType

    ALLURE_AVAILABLE = True
except ImportError:  # pragma: no cover - only hit in a misconfigured environment
    ALLURE_AVAILABLE = False

# ---------------------------------------------------------------------------
# Paths and constants
# ---------------------------------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parent
REPORTS_DIR = PROJECT_ROOT / "reports"
RUN_LOG_PATH = REPORTS_DIR / "pytest.log"

LOG_FORMAT = "%(asctime)s %(levelname)-8s [%(name)s] %(message)s"
LOG_DATE_FORMAT = "%Y-%m-%d %H:%M:%S"

# Keeps individual Allure attachments readable when a framework logs heavily.
MAX_ATTACHMENT_CHARS = 20_000

# Dedicated run-log logger.  ``propagate = False`` keeps framework bookkeeping
# lines out of per-test captured logs (and therefore out of Allure duplicates)
# while still writing them to the diagnostic run log.
RUN_LOGGER = logging.getLogger("framework.run")
RUN_LOGGER.propagate = False
RUN_LOGGER.setLevel(logging.INFO)

_STATUS_LABELS = {
    "passed": "PASSED",
    "failed": "FAILED",
    "skipped": "SKIPPED",
}

# If a test fails in more than one phase (for example a failed assertion that is
# followed by a teardown error), the most severe status is reported for that
# single selected test so the summary still adds up to the selected total.
_STATUS_PRECEDENCE = {
    "PASSED": 0,
    "SKIPPED": 1,
    "FAILED": 2,
    "ERROR": 3,
}

# ---------------------------------------------------------------------------
# Small helpers
# ---------------------------------------------------------------------------


def _distribution_version(name: str) -> str:
    try:
        return metadata.version(name)
    except metadata.PackageNotFoundError:
        return "not installed"
    except Exception:  # defensive: metadata must never break a test run
        return "unknown"


def _allure_results_dir(config: pytest.Config) -> Path | None:
    """Return the configured Allure results directory, if Allure is enabled."""

    configured = getattr(config.option, "allure_report_dir", None)
    if not configured:
        return None
    return Path(configured).expanduser().resolve()


def _truncate(text: str, limit: int = MAX_ATTACHMENT_CHARS) -> str:
    if len(text) <= limit:
        return text
    omitted = len(text) - limit
    return f"{text[:limit]}\n... [{omitted} characters omitted]"


def _attach_text(name: str, content: str) -> None:
    if not ALLURE_AVAILABLE or not content or not content.strip():
        return
    allure.attach(
        _truncate(content),
        name=name,
        attachment_type=AttachmentType.TEXT,
    )


def _attach_page_diagnostics(item: pytest.Item) -> None:
    """Attach a screenshot and current page state for browser test failures.

    Only UI tests request the pytest-playwright ``page`` fixture, so this is a
    no-op for the Django/BDD tests.  Every failure here is swallowed on purpose:
    report enrichment must never replace or mask the real test failure.
    """

    page = getattr(item, "funcargs", {}).get("page")
    if page is None:
        return

    state_lines = []
    try:
        state_lines.append(f"url: {page.url}")
    except Exception:  # noqa: BLE001 - diagnostics must not raise
        pass
    try:
        state_lines.append(f"title: {page.title()}")
    except Exception:  # noqa: BLE001 - diagnostics must not raise
        pass

    try:
        try:
            screenshot = page.screenshot(full_page=True)
        except Exception:  # noqa: BLE001 - fall back to viewport screenshot
            screenshot = page.screenshot()
        allure.attach(
            screenshot,
            name="failure screenshot",
            attachment_type=AttachmentType.PNG,
        )
    except Exception as error:  # noqa: BLE001 - diagnostics must not raise
        RUN_LOGGER.warning(
            "screenshot attachment skipped for %s: %s", item.nodeid, error
        )

    if state_lines:
        _attach_text("page state at failure", "\n".join(state_lines))


def _attach_captured_output(item: pytest.Item, report: pytest.TestReport) -> None:
    if getattr(item, "_framework_output_attached", False):
        return
    item._framework_output_attached = True  # type: ignore[attr-defined]

    _attach_text("captured log", getattr(report, "caplog", "") or "")
    _attach_text("captured stdout", getattr(report, "capstdout", "") or "")
    _attach_text("captured stderr", getattr(report, "capstderr", "") or "")


def _record_test_status(config: pytest.Config, report: pytest.TestReport) -> None:
    """Track one final status per selected test for the execution summary.

    Pytest emits separate setup/call/teardown reports.  Collapsing them into a
    single entry per node ID keeps ``passed + failed + skipped + errors`` equal
    to the number of selected test cases.
    """

    if report.when not in ("setup", "call", "teardown"):
        return

    if report.failed:
        status = "FAILED" if report.when == "call" else "ERROR"
    elif report.skipped:
        status = "SKIPPED"
    elif report.when == "call" and report.passed:
        status = "PASSED"
    else:
        return

    statuses = getattr(config, "_framework_test_statuses", None)
    if statuses is None:
        statuses = {}
        config._framework_test_statuses = statuses  # type: ignore[attr-defined]

    previous = statuses.get(report.nodeid)
    if previous is None or _STATUS_PRECEDENCE[status] >= _STATUS_PRECEDENCE[previous]:
        statuses[report.nodeid] = status


# ---------------------------------------------------------------------------
# Session configuration
# ---------------------------------------------------------------------------


def pytest_configure(config: pytest.Config) -> None:
    """Attach the per-run diagnostic log file.

    The file is opened before the session starts so collection errors and
    fixture problems are captured as well.  A failure to create the log must
    not prevent the tests from running.
    """

    if config.option.collectonly:
        return

    try:
        REPORTS_DIR.mkdir(parents=True, exist_ok=True)
        handler = logging.FileHandler(RUN_LOG_PATH, mode="w", encoding="utf-8")
        handler.setLevel(logging.INFO)
        handler.setFormatter(logging.Formatter(LOG_FORMAT, LOG_DATE_FORMAT))

        # Framework bookkeeping and regular application/test logs both go to
        # the run log; only the former bypasses pytest's capture machinery.
        logging.getLogger().addHandler(handler)
        RUN_LOGGER.addHandler(handler)

        config._framework_log_handler = handler  # type: ignore[attr-defined]
        RUN_LOGGER.info(
            "run started | rootdir=%s | cwd=%s", config.rootpath, os.getcwd()
        )
    except OSError as error:
        logging.getLogger("framework").warning(
            "run log disabled (%s): %s", RUN_LOG_PATH, error
        )


def pytest_unconfigure(config: pytest.Config) -> None:
    handler = getattr(config, "_framework_log_handler", None)
    if handler is None:
        return
    RUN_LOGGER.removeHandler(handler)
    logging.getLogger().removeHandler(handler)
    handler.close()
    del config._framework_log_handler  # type: ignore[attr-defined]


def pytest_sessionstart(session: pytest.Session) -> None:
    RUN_LOGGER.info(
        "environment | python=%s | platform=%s",
        platform.python_version(),
        platform.platform(),
    )


@pytest.hookimpl(tryfirst=True)
def pytest_collection_finish(session: pytest.Session) -> None:
    """Snapshot the final test selection for the user-facing summary.

    At this point marker filters, ``-k`` and explicit deselections have already
    been applied, so ``session.items`` contains only the test cases selected for
    this execution.

    Pytest's terminal reporter counts every collected item and appends
    ``"N deselected"`` to its collection and final status lines.  For normal
    executions the framework presents selected tests only, so the reporter is
    given the selected count and the deselected bucket is removed from its
    display stats.  The original discovery/selection numbers are preserved in
    the diagnostic run log instead.
    """

    config = session.config
    items = session.items
    config._framework_selected_total = len(items)  # type: ignore[attr-defined]
    config._framework_selected_has_ui = any(  # type: ignore[attr-defined]
        item.get_closest_marker("ui") for item in items
    )
    config._framework_selected_has_bdd = any(  # type: ignore[attr-defined]
        item.get_closest_marker("bdd") for item in items
    )

    if config.option.collectonly:
        return

    terminalreporter = config.pluginmanager.getplugin("terminalreporter")
    if terminalreporter is None:
        return

    discovered = getattr(terminalreporter, "_numcollected", len(items))
    deselected = len(getattr(terminalreporter, "stats", {}).get("deselected", []))
    RUN_LOGGER.info(
        "collection | discovered=%s selected=%s deselected=%s",
        discovered,
        len(items),
        deselected,
    )

    terminalreporter._numcollected = len(items)
    terminalreporter.stats.pop("deselected", None)


def pytest_sessionfinish(session: pytest.Session, exitstatus: int) -> None:
    """Write Allure metadata describing the environment that produced results.

    These files contain real environment information only; they never create or
    alter test results.
    """

    config = session.config
    if config.option.collectonly:
        return

    RUN_LOGGER.info("run finished | exit status=%s", exitstatus)

    results_dir = _allure_results_dir(config)
    if results_dir is None or not ALLURE_AVAILABLE:
        return

    browser = getattr(config.option, "browser", None) or ["chromium"]
    browser_mode = "headed" if getattr(config.option, "headed", False) else "headless"

    environment = {
        "Framework": "Django Blog web UI test automation",
        "Python": platform.python_version(),
        "Platform": platform.platform(),
        "Pytest": _distribution_version("pytest"),
        "Django": _distribution_version("Django"),
        "pytest-django": _distribution_version("pytest-django"),
        "pytest-playwright": _distribution_version("pytest-playwright"),
        "pytest-bdd": _distribution_version("pytest-bdd"),
        "allure-pytest": _distribution_version("allure-pytest"),
        "Browser": ", ".join(browser),
        "Browser mode": browser_mode,
        "Application under test": "Django live_server fixture",
        "Database": "pytest-django test database (SQLite)",
    }

    categories = [
        {
            "name": "FAILED - assertion did not match expected result",
            "matchedStatuses": ["failed"],
            "messageRegex": ".*",
        },
        {
            "name": "ERROR - setup, fixture, browser or teardown problem",
            "matchedStatuses": ["broken"],
            "messageRegex": ".*",
        },
    ]

    try:
        results_dir.mkdir(parents=True, exist_ok=True)
        (results_dir / "environment.properties").write_text(
            "".join(f"{key}={value}\n" for key, value in environment.items()),
            encoding="utf-8",
        )
        (results_dir / "categories.json").write_text(
            json.dumps(categories, indent=2) + "\n",
            encoding="utf-8",
        )
    except OSError as error:
        RUN_LOGGER.warning("Allure environment metadata not written: %s", error)


# ---------------------------------------------------------------------------
# Terminal header
# ---------------------------------------------------------------------------


def pytest_report_header(config: pytest.Config) -> list[str]:
    """Add only framework-specific information to pytest's own header."""

    browser = ", ".join(getattr(config.option, "browser", None) or ["chromium"])
    browser_mode = "headed" if getattr(config.option, "headed", False) else "headless"
    allure_dir = _allure_results_dir(config)

    return [
        "framework: Django Blog test automation",
        f"browser: {browser} ({browser_mode})",
        f"allure: {allure_dir if allure_dir else 'disabled'}",
        f"run log: {RUN_LOG_PATH}",
    ]


# ---------------------------------------------------------------------------
# Selected-test execution summary
# ---------------------------------------------------------------------------


def pytest_terminal_summary(
    terminalreporter: pytest.TerminalReporter,
    exitstatus: int,
    config: pytest.Config,
) -> None:
    """Print a summary that counts only tests selected for this execution.

    Pytest's collection line still shows how many tests were discovered and
    deselected; this block deliberately reports only the final selection so
    marker-filtered runs are not presented with the full repository total.
    """

    if config.option.collectonly:
        return

    total = getattr(config, "_framework_selected_total", None)
    if total is None:
        return

    statuses = getattr(config, "_framework_test_statuses", {})
    counts = {name: 0 for name in ("PASSED", "FAILED", "SKIPPED", "ERROR")}
    for status in statuses.values():
        counts[status] += 1

    has_ui = getattr(config, "_framework_selected_has_ui", False)
    has_bdd = getattr(config, "_framework_selected_has_bdd", False)
    if has_ui and not has_bdd:
        title = "UI TEST EXECUTION SUMMARY"
    elif has_bdd and not has_ui:
        title = "BDD TEST EXECUTION SUMMARY"
    else:
        title = "TEST EXECUTION SUMMARY"

    terminalreporter.write_line("")
    terminalreporter.write_line(title, bold=True)
    terminalreporter.write_line("")
    terminalreporter.write_line(f"Total Test Cases: {total}")
    terminalreporter.write_line(f"Passed: {counts['PASSED']}")
    terminalreporter.write_line(f"Failed: {counts['FAILED']}")
    terminalreporter.write_line(f"Skipped: {counts['SKIPPED']}")
    terminalreporter.write_line(f"Errors: {counts['ERROR']}")

    RUN_LOGGER.info(
        "summary | selected=%s passed=%s failed=%s skipped=%s errors=%s",
        total,
        counts["PASSED"],
        counts["FAILED"],
        counts["SKIPPED"],
        counts["ERROR"],
    )


# ---------------------------------------------------------------------------
# Per-test reporting
# ---------------------------------------------------------------------------


def pytest_runtest_logreport(report: pytest.TestReport) -> None:
    """Write one concise status line per test to the diagnostic run log."""

    if report.when == "call":
        status = _STATUS_LABELS.get(report.outcome, report.outcome.upper())
    elif report.skipped:
        status = "SKIPPED"
    elif report.failed:
        # A failure outside the call phase is an execution error (fixture,
        # browser, database or teardown), not a failed assertion.
        status = "ERROR"
    else:
        return

    RUN_LOGGER.info(
        "%s %s (%.2fs, phase=%s)",
        status,
        report.nodeid,
        report.duration,
        report.when,
    )


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item: pytest.Item, call: pytest.CallInfo):
    """Enrich failed reports with diagnostics without changing the outcome."""

    outcome = yield
    report = outcome.get_result()

    try:
        _record_test_status(item.config, report)
    except Exception as error:  # noqa: BLE001 - reporting must never break a run
        RUN_LOGGER.warning(
            "status tracking failed for %s: %s", item.nodeid, error
        )

    if not report.failed or not ALLURE_AVAILABLE:
        return

    try:
        if report.when == "call":
            _attach_page_diagnostics(item)
        _attach_captured_output(item, report)
    except Exception as error:  # noqa: BLE001 - reporting must never break a run
        RUN_LOGGER.warning(
            "Allure diagnostics attachment failed for %s: %s", item.nodeid, error
        )
