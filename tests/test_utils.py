import pytest

from elmo.utils import _camel_to_snake_case, _filter_data, _sanitize_session_id


def test_filter_data_empty_data():
    """Tests the _filter_data function with an empty data dictionary."""
    data = {}
    key = "test_key"
    status = True
    assert _filter_data(data, key, status) == {}


def test_filter_data_status_true():
    """Tests the _filter_data function when status is True."""
    data = {"test_key": {"item1": {"status": True}, "item2": {"status": False}}}
    key = "test_key"
    status = True
    assert _filter_data(data, key, status) == {"item1": {"status": True}}


def test_filter_data_status_false():
    """Tests the _filter_data function when status is False."""
    data = {"test_key": {"item1": {"status": True}, "item2": {"status": False}}}
    key = "test_key"
    status = False
    assert _filter_data(data, key, status) == {"item2": {"status": False}}


def test_filter_data_empty_key():
    """Tests the _filter_data function with an empty key string."""
    data = {"test_key": {"item1": {"status": True}, "item2": {"status": False}}}
    key = ""
    status = True
    assert _filter_data(data, key, status) == {}


def test_filter_data_none_status():
    """Tests the _filter_data function with a None status value."""
    data = {"test_key": {"item1": {"status": True}, "item2": {"status": False}}}
    key = "test_key"
    status = None
    assert _filter_data(data, key, status) == {}


def test_filter_data_nested_data():
    """Tests the _filter_data function with nested data dictionary."""
    data = {"test_key": {"item1": {"status": True, "subitem": {"status": False}}, "item2": {"status": False}}}
    key = "test_key"
    status = False
    assert _filter_data(data, key, status) == {"item2": {"status": False}}


def test_filter_data_multiple_keys():
    """Tests the _filter_data function with multiple keys in data dictionary."""
    data = {"key1": {"item1": {"status": True}}, "key2": {"item2": {"status": False}}}
    key = "key1"
    status = True
    assert _filter_data(data, key, status) == {"item1": {"status": True}}


def test_filter_data_key_error():
    """Tests the _filter_data function raising a KeyError."""
    data = {"test_key": {"item1": {"status": True}, "item2": {"status": False}}}
    key = "invalid_key"
    status = True
    with pytest.raises(KeyError):
        _filter_data(data, key, status)


def test_sanitize_identifier():
    """Ensure session ID are obfuscated for debug purposes."""
    assert _sanitize_session_id("0fb182e9-474c-ca1c-f60c-ed203dbb26aa") == "0fb182e9-XXXX-XXXX-XXXX-XXXXXXXXXXXX"
    assert _sanitize_session_id("abcdefgh-ijkl-mnop-qrst-uvwxyz012345") == "abcdefgh-XXXX-XXXX-XXXX-XXXXXXXXXXXX"
    assert _sanitize_session_id("12345678-90ab-cdef-ghij-klmnopqrstuv") == "12345678-XXXX-XXXX-XXXX-XXXXXXXXXXXX"


def test_camel_to_snake_case_single_word():
    """Test conversion of a single capitalized word."""
    assert _camel_to_snake_case("Camel") == "camel"


def test_camel_to_snake_case_multiple_words():
    """Test conversion of a camel-cased string with multiple words."""
    assert _camel_to_snake_case("CamelCaseString") == "camel_case_string"


def test_camel_to_snake_case_multiple_words_alt():
    """Test conversion of a camel-cased string with multiple words (alternative)."""
    assert _camel_to_snake_case("camelCaseString") == "camel_case_string"


def test_camel_to_snake_case_single_letter():
    """Test conversion of a single capitalized letter."""
    assert _camel_to_snake_case("C") == "c"


def test_camel_to_snake_case_empty_string():
    """Test conversion of an empty string."""
    assert _camel_to_snake_case("") == ""


def test_camel_to_snake_case_already_snake_case():
    """Test conversion of a string already in snake case."""
    assert _camel_to_snake_case("already_snake_case") == "already_snake_case"


def test_camel_to_snake_case_mixed_casing():
    """Test conversion of a string with mixed casing."""
    assert _camel_to_snake_case("mixedCasing_isHERE") == "mixed_casing_is_here"


def test_camel_to_snake_case_with_numbers():
    """Test conversion of a camel-cased string with numbers."""
    assert _camel_to_snake_case("CamelCase1With2Numbers") == "camel_case_1_with_2_numbers"


def test_camel_to_snake_case_with_symbols():
    """Test conversion of a camel-cased string with numbers."""
    assert _camel_to_snake_case("CamelCase-With-symbols") == "camel_case_with_symbols"


def test_camel_to_snake_case_all_uppercase():
    """Test conversion of an all-uppercase string."""
    assert _camel_to_snake_case("UPPERCASE") == "uppercase"


def test_camel_to_snake_case_cache(mocker):
    """Test that cached values don't call regex twice."""
    mocked_sub = mocker.patch("re.sub")
    _camel_to_snake_case("camelCase")
    _camel_to_snake_case("camelCase")
    assert mocked_sub.call_count == 4
