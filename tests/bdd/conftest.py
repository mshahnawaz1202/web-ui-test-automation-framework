def pytest_configure(config):
    """Register the tags used by the Gherkin feature files as pytest markers."""
    for number in range(1, 17):
        config.addinivalue_line(
            "markers",
            f"BDD-{number:03d}: Gherkin scenario BDD-{number:03d}",
        )
    for feature_tag in (
        "registration",
        "authentication",
        "blog_viewing",
        "blog_creation",
        "profile",
    ):
        config.addinivalue_line(
            "markers",
            f"{feature_tag}: Gherkin feature tag {feature_tag}",
        )
