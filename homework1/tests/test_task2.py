# parameterized tests verifying the value and type returned from task2 functions
import pytest

from task2 import add_integers, divide, is_even, caps


@pytest.mark.parametrize(
    "func, args, expected, expected_type",
    [
        (add_integers, (2, 3), 5, int),
        (add_integers, (-4, 4), 0, int),
        # true division always returns a float, even when it divides evenly
        (divide, (7, 2), 3.5, float),
        (divide, (9, 3), 3.0, float),
        (caps, ("hello",), "HELLO!", str),
        (caps, ("",), "!", str),
        (is_even, (4,), True, bool),
        (is_even, (7,), False, bool),
    ],
)
def test_returns_expected_value_and_type(func, args, expected, expected_type):
    result = func(*args)
    assert result == expected
    assert type(result) is expected_type