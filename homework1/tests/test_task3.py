# tests for the if statement, for loop, and while loop in task 3
# with edge cases

from task3 import classify_number, first_n_primes, is_prime, sum_to


def test_classify_positive():
    assert classify_number(5) == "positive"
    assert classify_number(0.5) == "positive"


def test_classify_negative():
    assert classify_number(-5) == "negative"
    assert classify_number(-0.5) == "negative"


def test_classify_zero():
    assert classify_number(0) == "zero"


def test_is_prime_true():
    assert is_prime(2) is True
    assert is_prime(3) is True
    assert is_prime(29) is True


def test_is_prime_false():
    assert is_prime(4) is False
    assert is_prime(9) is False


def test_is_prime_edge_cases():
    # neg, zero, one
    assert is_prime(0) is False
    assert is_prime(1) is False
    assert is_prime(-7) is False

# confirm functions...
def test_first_ten_primes():
    assert first_n_primes() == [2, 3, 5, 7, 11, 13, 17, 19, 23, 29]


def test_first_n_primes_other_counts():
    assert first_n_primes(3) == [2, 3, 5]
    # asking for zero primes should return an empty list
    assert first_n_primes(0) == []


def test_sum_to_100():
    assert sum_to() == 5050


def test_sum_to_edge_cases():
    assert sum_to(1) == 1
    assert sum_to(10) == 55
    # loop body never runs when limit is invalid..
    assert sum_to(0) == 0
    assert sum_to(-5) == 0