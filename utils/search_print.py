import os

file = "../newmenus.py"
fd = open(file, 'r')
index = 0
while True:
    index += 1
    line = fd.readline()
    if not line:
        break
    line = line.strip()
    if (line.startswith("print")):
        print(("line: %d; %s"% (index, line)))