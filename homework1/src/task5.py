# list of favorite books as (title, author) tuples
favorite_books = [
    ("The Giving Tree", "Shel Silverstein"),
    ("Dungeon Crawler Carl", "Matt Dinnimon"),
    ("Harry Potter", "J.K. Rowling"),
    ("The Martian", "Andy Weir"),
    ("Project Hail Mary", "Andy Weir"),
]

# student database, name mapped to student id
student_database = {
    "Alice Andrew": 1001,
    "Bob Butters": 1002,
    "Eve Elders": 1003,
    "Jackson Robert": 1004,
}

#slicing to return first 3 in list
def first_three_books(books=None):
    if books is None:
        books = favorite_books
    return books[:3]

# fetch the id
def get_student_id(name, database=None):
    if database is None:
        database = student_database
    return database.get(name)

if __name__ == "__main__":
    for title, author in first_three_books():
        print(title, "by", author)
    print(student_database)
    print(get_student_id("Bob Butters"))