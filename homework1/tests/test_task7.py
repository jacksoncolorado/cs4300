# tests for numpy task7
import pytest

from task7 import array_mean, array_stats, scale

# assert the tests
def test_array_mean():
    assert array_mean([1, 2, 3, 4]) == pytest.approx(2.5)

def test_array_mean_floats():
    assert array_mean([1.5, 2.5]) == pytest.approx(2.0)

def test_array_stats():
    assert array_stats([5, 1, 9]) == {"min": 1.0, "max": 9.0, "sum": 15.0}

def test_scale():
    assert scale([1, 2, 3], 3) == [3, 6, 9]

# edge (kinda)
def test_scale_by_zero():
    assert scale([1, 2, 3], 0) == [0, 0, 0]

# should return nan for empty array
def test_empty_array_mean_is_nan():
    import math

    # remove warning for nan
    with pytest.warns(RuntimeWarning):
        result = array_mean([])
    assert math.isnan(result)