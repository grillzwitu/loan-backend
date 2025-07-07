"""Module: Directly load and execute loan/views.py to cover import and __all__ lines."""

import importlib.util
import os

import pytest


@pytest.mark.django_db
def test_import_views_py_module() -> None:
    """
    Load loan/views.py via importlib to execute its top-level imports and __all__.
    """
    # Determine path to loan/views.py
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../"))
    file_path = os.path.join(base_dir, "loan", "views.py")

    # Load module spec from file location
    spec = importlib.util.spec_from_file_location("loan_views_module", file_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)

    # Verify each name in __all__ is present on the module
    for view_name in getattr(module, "__all__", []):
        assert hasattr(module, view_name), f"{view_name} not found in loaded module"
