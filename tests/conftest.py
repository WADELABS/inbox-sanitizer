"""Pytest configuration for inbox-sanitizer tests"""

import pytest

def pytest_collection_modifyitems(items):
    """
    Modify test collection to filter out non-test functions from src modules.
    This prevents pytest from collecting test_connection from src.auth as a test.
    """
    filtered_items = []
    for item in items:
        # Skip items that are collected from src/ directory
        if 'src/' in str(item.fspath) or 'src\\' in str(item.fspath):
            continue
        filtered_items.append(item)
    items[:] = filtered_items
