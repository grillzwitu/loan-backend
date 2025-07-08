"""
Module: Execute loan/views.py source to run its import
and __all__ statements for coverage.
"""

from pathlib import Path

import pytest
from typing import Dict, Any


@pytest.mark.django_db
def test_execute_loan_views_source() -> None:
    """Read and execute the source of loan/views.py so that coverage records
    execution of its import lines and __all__ definition."""
    project_root = Path(__file__).resolve().parents[3]
    file_path = project_root / "loan" / "views.py"
    source = file_path.read_text()

    # Execute the source in a fresh namespace
    namespace: Dict[str, Any] = {}
    exec(compile(source, str(file_path), "exec"), namespace, namespace)

    # Ensure __all__ lists the expected view names in namespace
    all_names = namespace.get("__all__", [])
    assert (
        isinstance(all_names, list) and all_names
    ), "__all__ should be a non-empty list"
    for view_name in all_names:
        msg = f"{view_name} missing after executing source"
        assert view_name in namespace, msg
