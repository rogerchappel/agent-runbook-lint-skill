"""Repository-wide pytest collection safeguards."""

MINIMUM_TEST_COUNT = 84


def pytest_collection_finish(session) -> None:
    """Fail collection when canonical test modules disappear or stop matching."""
    collected = len(session.items)
    if collected < MINIMUM_TEST_COUNT:
        session.exitstatus = 1
        reporter = session.config.pluginmanager.get_plugin("terminalreporter")
        if reporter is not None:
            reporter.write_line(
                f"ERROR: expected at least {MINIMUM_TEST_COUNT} collected tests; found {collected}.",
                red=True,
            )
