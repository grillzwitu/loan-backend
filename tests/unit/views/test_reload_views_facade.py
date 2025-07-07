"""
Module: Unit tests for loan.views facade reload.

This module validates the facade pattern for loan views by:

- Verifying the presence and structure of the __all__ attribute, ensuring it defines the public API.
- Reloading the facade module to exercise its import statements and confirm they execute without error.
- Ensuring every view class name listed in __all__ is exposed as an attribute on the module after reload.

Such tests guarantee that re-exported view implementations in loan.views remain consistent and complete.
"""

import importlib

import pytest

import loan.views as views


@pytest.mark.django_db
def test_reload_views_facade_exports_all_view_classes() -> None:
    """
    Reload the loan.views facade module and confirm:
      - __all__ is present and lists the expected view class names.
      - Each view name in __all__ is available as an attribute on the module.
    """
    # Verify existing __all__
    facade_all = getattr(views, "__all__", None)
    assert facade_all is not None, "__all__ attribute is missing"
    assert isinstance(facade_all, list), "__all__ must be a list"
    assert facade_all, "__all__ list should not be empty"

    # Reload module to execute import lines again
    reloaded = importlib.reload(views)

    # Confirm each view name in __all__ resolves on the reloaded module
    for view_name in reloaded.__all__:
        assert hasattr(
            reloaded, view_name
        ), f"Expected view '{view_name}' not found in reloaded module"
