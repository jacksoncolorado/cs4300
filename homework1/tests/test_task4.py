# tests for calculate_discount with different numeric types
from decimal import Decimal
from fractions import Fraction
import pytest # raises, aprox

from task4 import calculate_discount
# ints
def test_integers():
    assert calculate_discount(100, 20) == 80

#floats
def test_floats():
    assert calculate_discount(100.0, 25.5) == pytest.approx(74.5)

# both
def test_mixed_int_and_float():
    assert calculate_discount(100, 12.5) == pytest.approx(87.5)
    assert calculate_discount(80.0, 10) == pytest.approx(72.0)

# decimal isnt int or float but does math
def test_decimal_type():
    assert calculate_discount(Decimal("100"), Decimal("10")) == Decimal("90")

# duk test for frac
def test_fraction_type():
    # Fraction is another unrelated numeric type that works the same way
    assert calculate_discount(Fraction(100), Fraction(50)) == Fraction(50)

# edge
def test_no_discount():
    assert calculate_discount(100, 0) == 100

# edge
def test_full_discount():
    assert calculate_discount(100, 100) == 0

# error types
def test_non_numeric_raises_type_error():
    with pytest.raises(TypeError):
        calculate_discount("100", 20)
    with pytest.raises(TypeError):
        calculate_discount(100, None)

# bool thrown in
def test_bool_raises_type_error():
    with pytest.raises(TypeError):
        calculate_discount(True, 20)

# edge
def test_negative_price_raises_value_error():
    with pytest.raises(ValueError):
        calculate_discount(-100, 20)

# range tests
def test_discount_out_of_range_raises_value_error():
    with pytest.raises(ValueError):
        calculate_discount(100, -5)
    with pytest.raises(ValueError):
        calculate_discount(100, 150)