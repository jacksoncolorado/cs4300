import subprocess
import sys

def test_hello_world():
    result = subprocess.run([sys.executable, "src/task1.py"], capture_output=True, text=True)
    assert result.stdout == "Hello, World!\n"