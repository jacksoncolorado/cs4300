# read a text file and count the words in it
from pathlib import Path

# AI said to do this for resolving path relative to this file so it works from any directory
DEFAULT_FILE = Path(__file__).resolve().parent.parent / "task6_read_me.txt"

# whitespace check for word count!
def count_words(path=DEFAULT_FILE):
    with open(path, encoding="utf-8") as file:
        return len(file.read().split())


if __name__ == "__main__":
    print(count_words())