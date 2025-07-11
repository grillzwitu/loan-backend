"""
Module: Directly load and execute loan/views.py to cover import
and __all__ lines.
"""

import importlib.util
import os

import pytest
from importlib.machinery import ModuleSpec
from typing import cast


@pytest.mark.django_db
def test_import_views_py_module() -> None:
    """
    Load loan/views.py via importlib to execute its top-level imports
    and __all__.
    """
    # Determine path to loan/views.py
    base_dir = os.path.abspath(
        os.path.join(
            os.path.dirname(__file__),
            "../../../"
        )
    )
    file_path = os.path.join(base_dir, "loan", "views.py")

    # Load module spec from file location
    spec = importlib.util.spec_from_file_location(
        "loan_views_module",
        file_path,
    )
    assert spec is not None, f"Failed to load ModuleSpec for {file_path}"
    spec = cast(ModuleSpec, spec)
    module = importlib.util.module_from_spec(spec)
    loader = spec.loader
    assert loader is not None, "ModuleSpec loader is missing"
    loader.exec_module(module)

    # Verify each name in __all__ is present on the module
    for view_name in getattr(module, "__all__", []):
        msg = f"{view_name} not found in loaded module"
        assert hasattr(module, view_name), msg
