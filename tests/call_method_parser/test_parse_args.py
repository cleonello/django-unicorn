from uuid import UUID

import pytest

from django_unicorn.call_method_parser import parse_args


def test_args():
    expected = [1, 2]
    actual = parse_args("1, 2")

    assert actual == expected
    assert isinstance(actual[0], int)
    assert isinstance(actual[1], int)


def test_single_quote_str_arg():
    expected = ["1"]
    actual = parse_args("'1'")

    assert actual == expected
    assert isinstance(actual[0], str)


def test_str_with_space_arg():
    expected = ["django unicorn"]
    actual = parse_args("'django unicorn'")

    assert actual == expected
    assert isinstance(actual[0], str)


def test_str_with_extra_single_quote():
    expected = ["django's unicorn"]
    actual = parse_args("'django's unicorn'")

    assert actual == expected
    assert isinstance(actual[0], str)


def test_str_with_extra_double_quote():
    expected = ['django "unicorn"']
    actual = parse_args("'django \"unicorn\"'")

    assert actual == expected
    assert isinstance(actual[0], str)


@pytest.mark.skip("These are edge cases, but still are broken")
def test_str_with_comma():
    expected = ["a', b"]
    actual = parse_args("'a', b'")

    assert actual == expected
    assert isinstance(actual[0], str)


@pytest.mark.skip("These are edge cases, but still are broken")
def test_str_with_stop_character():
    expected = ["a'} b"]
    actual = parse_args("'a'} b'")

    assert actual == expected
    assert isinstance(actual[0], str)


def test_double_quote_str_arg():
    expected = ["string"]
    actual = parse_args('"string"')

    assert actual == expected
    assert isinstance(actual[0], str)


def test_args_with_single_quote_dict():
    expected = [1, {"2": 3}]
    actual = parse_args("1, {'2': 3}")

    assert actual == expected
    assert isinstance(actual[1], dict)


def test_args_with_double_quote_dict():
    expected = [1, {"2": 3}]
    actual = parse_args('1, {"2": 3}')

    assert actual == expected
    assert isinstance(actual[1], dict)


def test_args_with_nested_dict():
    expected = [1, {"2": {"3": 4}}]
    actual = parse_args("1, {'2': { '3': 4 }}")

    assert actual == expected
    assert isinstance(actual[1], dict)
    assert isinstance(actual[1].get("2"), dict)


def test_args_with_nested_list_3():
    expected = [[1, ["2", "3"], 4], 9]
    actual = parse_args("[1, ['2', '3'], 4], 9")

    assert actual == expected


def test_args_with_nested_tuple():
    expected = [9, (1, ("2", "3"), 4)]
    actual = parse_args("9, (1, ('2', '3'), 4)")

    assert actual == expected


def test_args_with_nested_objects():
    expected = [[0, 1], {"2 2": {"3": 4}}, (5, 6, [7, 8])]
    actual = parse_args("[0,  1], {'2 2': { '3': 4 }}, (5, 6, [7, 8])")

    assert actual == expected


def test_list_args():
    expected = [1, [2, "3"]]
    actual = parse_args("1, [2, '3']")

    assert actual == expected


from datetime import datetime


def test_datetime():
    expected = [datetime(2020, 9, 12, 1, 1, 1)]
    actual = parse_args("2020-09-12T01:01:01")

    assert actual == expected
    assert isinstance(actual[0], datetime)


def test_uuid():
    expected = [UUID("90144cb9-fc47-476d-b124-d543b0cff091")]
    actual = parse_args("90144cb9-fc47-476d-b124-d543b0cff091")

    assert actual == expected
    assert isinstance(actual[0], UUID)


def test_float():
    expected = [[1, 5.4]]
    actual = parse_args("[1, 5.4]")

    assert actual == expected
    assert isinstance(actual[0][1], float)


def test_set():
    expected = [{1, 5}]
    actual = parse_args("{1, 5}")

    assert actual == expected
    assert isinstance(actual[0], set)
