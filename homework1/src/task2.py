# demonstrate python's core data types and their behavior

# ints
def add_integers(a, b):
    return a + b

# float test
def divide(a, b):
    return a / b

# making a strong uppercased
def caps(text):
    return text.upper() + "!"

# bool test, True if even , False otherwise
def is_even(number):
    return number % 2 == 0


if __name__ == "__main__":
    print(add_integers(2, 3), type(add_integers(2, 3)))
    print(divide(7, 2), type(divide(7, 2)))
    print(caps("hello"), type(caps("hello")))
    print(is_even(4), type(is_even(4)))