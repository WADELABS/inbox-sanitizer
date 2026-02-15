"""Pytest configuration for inbox-sanitizer tests"""

import pytest

def pytest_collection_modifyitems(config, items):
    """
    Modify test collection to filter out non-test functions from src modules.
    This prevents pytest from collecting test_connection from src.auth as a test.
    """
    # Filter out any test items that come from the src/ directory  
    filtered = []
    for item in items:
        # Check if the item is from src/auth.py
        fspath = str(item.fspath)
        # Also check the nodeid which shows where the test was collected from
        if 'src/auth.py' in fspath or (hasattr(item, 'function') and 
                                       hasattr(item.function, '__module__') and 
                                       'src.auth' in item.function.__module__ and
                                       item.function.__name__ == 'test_connection'):
            continue  # Skip this item
        filtered.append(item)
    
    items[:] = filtered
