# cusorx Module

This is a lightweight text manipulation engine built around a cursor-based module.

Allows precise control over text editing operations.

## Features

- Cursor Movement (forward, backword, word-based, char-based)

-Text selection (range, word, line, char)

-Insert / Replace / Delete operations

-Undo / Redo System

-Clipboard system (copy, cut, paste)

-Snapshots for debugging

-Chainable API design

---

## installation

```
pip install cursor

```

## Basic usage

```python
import cursorx as cx

c= cx.Cursor("Hello world")
c.mov(6) # -> cursor now at w
c.select_word() # -> selects the word 'world'

print(c.selected_text) # world

c.replace_text("CursorX")
print(c.return_text) # > replaces world with CursorX

```
