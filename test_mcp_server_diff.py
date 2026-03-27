import pytest
from mcp_server_diff import apply_diff

def test_apply_diff_not_found():
    content = "This is a test string."
    search_block = "not found"
    replace_block = "replacement"
    with pytest.raises(ValueError) as e:
        apply_diff(content, search_block, replace_block)
    assert str(e.value) == "Could not find the search block in the file. Ensure the search block exactly matches the existing code."

def test_apply_diff_empty_search_block():
    content = "This is a test string."
    search_block = ""
    replace_block = "replacement"
    with pytest.raises(ValueError) as e:
        apply_diff(content, search_block, replace_block)
    assert str(e.value) == "Search block is effectively empty."

def test_apply_diff_invalid_replacement():
    content = "This is a test string."
    search_block = "test"
    replace_block = None
    with pytest.raises(TypeError) as e:
        apply_diff(content, search_block, replace_block)
    assert str(e.value) == "replace_block must be a string"
