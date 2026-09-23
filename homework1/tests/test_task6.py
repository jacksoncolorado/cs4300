# tests for the word counter
import pytest
from task6 import count_words

# paramaterized tests.. 
# extra whitespace/line/tab should raise count
@pytest.mark.parametrize(
    "text, expected",
    [
        ("", 0), ("one", 1), ("two words", 2),
        ("one  one \n text \t here ", 4),
    ],
)

# assert word counter
def test_count_words(tmp_path, text, expected):
    # tmp_path gives a fresh temp directory per test
    temp_file = tmp_path / "sample.txt"
    temp_file.write_text(text, encoding="utf-8")
    assert count_words(temp_file) == expected

# verify word count
def test_read_me_file():
    assert count_words() == 104

# error handle
def test_missing_file_raises():
    with pytest.raises(FileNotFoundError):
        count_words("does_not_exist.txt")