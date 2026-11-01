# main.py
from tools.parser import parse_command
from tools.execute import execute

print("Hello, Sir. Janet is online.")

while True:
    execute(parse_command())
