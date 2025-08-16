import os
import pytest


def pytest_collection_modifyitems(config, items):
    """Auto-mark and optionally skip e2e/integration/service-heavy tests.

    Skips when env RUN_REQUIRES_SERVICES is not truthy.
    """
    run_services = os.getenv("RUN_REQUIRES_SERVICES", "0").lower() in ("1", "true", "yes")

    service_patterns = (
        "/e2e/",
        "tests/e2e/",
        "user_journey",
        "search_perplexity",
        "turnitin",
        "autonomy_v2",
        "integration/",
    )

    for item in items:
        nodeid = item.nodeid.lower()
        is_service_heavy = any(p in nodeid for p in service_patterns)

        if is_service_heavy:
            item.add_marker(pytest.mark.requires_services)
            item.add_marker(pytest.mark.integration)
            if not run_services:
                item.add_marker(pytest.mark.skip(reason="Requires external services (DB/Redis/API). Set RUN_REQUIRES_SERVICES=1 to enable."))

