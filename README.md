# cs4300
# ------------------------------------------------------------------------
# homework 1

This is an introduction to python and unit testing. 
seven tasks covering:  data types, control structures, duck typing, 
lists and dictionaries, file handling, and package management, each with pytest test cases.

## requirements

- python 3.12
- pytest
- numpy

## setup

```bash
python3 -m venv hw1env --system-site-packages
source hw1env/bin/activate
python3 -m pip install pytest numpy
```

## running the code

each task runs on its own:

```bash
python3 src/task1.py
python3 src/task2.py
python3 src/task3.py
python3 src/task4.py
python3 src/task5.py
python3 src/task6.py
python3 src/task7.py
```

## running the tests

from inside the homework1 directory:

```bash
pytest -v
```

## tasks

- task 1: prints "Hello, World!", tested by running the script and capturing stdout
- task 2: integer, float, string, and boolean functions, parameterized tests
- task 3: if statement for positive/negative/zero, for loop for the first 10 primes, while loop summing 1 to 100
- task 4: calculate_discount using duck typing, accepts any numeric type, validates its input
- task 5: list of favorite books with slicing, dictionary of student names to ids
- task 6: counts the words in task6_read_me.txt, parameterized tests using temp files
- task 7: numpy for array statistics
# ------------------------------------------------------------------------
