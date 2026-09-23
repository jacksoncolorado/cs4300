# tests for the list and dictionary ops
from task5 import (
    favorite_books,
    first_three_books,
    get_student_id,
    student_database,
)

# verify list is correct an dgive title and author pairing
def test_book_list_structure():
    assert isinstance(favorite_books, list)
    for book in favorite_books:
        assert len(book) == 2


# slice check for 3 book return
def test_slicing_returns_three():
    result = first_three_books()
    assert len(result) == 3
    assert result == favorite_books[:3]

# order check
def test_slicing_keeps_order():
    assert first_three_books()[0] == favorite_books[0]

# shortened list check
def test_slicing_short_list():
    # slicing past the end does not error, it just returns what exists
    assert first_three_books([("A", "B")]) == [("A", "B")]
    assert first_three_books([]) == []

# verify student database... 
def test_student_database_structure():
    assert isinstance(student_database, dict)
    for name, student_id in student_database.items():
        assert isinstance(name, str)
        assert isinstance(student_id, int)


# lookup
def test_lookup_existing_student():
    assert get_student_id("Alice Andrew") == 1001

# lookup void
def test_lookup_missing_student():
    # get returns None instead of raising KeyError
    assert get_student_id("Nobody Here") is None