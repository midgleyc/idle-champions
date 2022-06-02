#!/bin/env python3
import sys

def main(filename):
  with open(filename, 'rb') as f:
    s = f.read()
  try:
    i = s.index(b'PNG')
  except ValueError:
    return
  if (i > 0):
    s = s[i - 1:]
    with open(filename, 'wb') as f:
      f.write(s)

if __name__ == '__main__':
  main(sys.argv[1])
