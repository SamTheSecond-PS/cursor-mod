import re

class NoSelectionError(Exception):
    pass


MAX_CLIPBOARD = 50
MAX_HISTORY = 100

'''beginning of the main class'''

class Cursor:
    
    '''INITIALIZATION'''
    def __init__(self, text: str):
        # This is where the text you edit is defined
        if isinstance(text, str):
            self._text = text
        else:
            raise TypeError(f"Expected str for Cursor, got {type(text).__name__}")
        # This is the index at which your on in the text
        self.pos = 0
        # This is how selection works, this define the specific amt of chars you selected
        self.selection = None
        # This is for the selection, this defines the position from which you start selecting
        self._last_pos = 0
        # This is used in undo for keeping a record of actions you did
        self._history = []
        # This is used in redo for keeping a record of actions
        self._redo_stack = []
        # This is for keeping the copied\cutted sentence sentence
        self.clipboard = []

    '''HELPERS'''
    
    # This saves the last action you do and clears the redo
    def _save_state(self, action_type: str, pos: int, text):
        '''Saves state for use of other functions'''
        self._history.append((action_type, pos, text))
        if len(self._history) > MAX_HISTORY:
                self._history.pop(0)
        self._redo_stack.clear()
    
    # helper function for tab and enter
    def __insert_char(self, text: str) -> "Cursor":

        '''Inserts a character at current position, used by tab and enter.'''
        self._save_state("insert", self.pos, text)
        before = self._text[:self.pos]
        after = self._text[self.pos:]
        self._text = f"{before}{text}{after}"
        self.pos += len(text)
        return self
    
    
    '''MOVEMENT'''

    # This moves the position until a specific character is found
    def mov_until_char(self, char: str) -> "Cursor":
        '''Functions moves the cursor until a specific char is found.'''
        self._last_pos = self.pos  
        found = self._text.find(char, self.pos)
        if found == -1:
            found = len(self._text)
        self.pos = found
        return self

    # Moves forward until any item in a list is found
    def mov_until_any(self, chars: list) -> "Cursor":
        '''Keeps moving the cursor until any char from the list is found'''
        self._last_pos = self.pos

        for i in range(self.pos, len(self._text)):
            if self._text[i] in chars:
                self.pos = i
                return self
            
        self.pos = len(self._text)
        return self
    
    # Moves forward until any item in a list is found
    def back_until_any(self, chars: list) -> "Cursor":
        '''Moves backwards until any char from a list is found.'''
        self._last_pos = self.pos

        for i in range(self.pos-1, -1, -1):
            if self._text[i] in chars:
                self.pos = i
                return self
        
        self.pos = 0
        return self

    # Resets the position of self.pos to 0
    def restart(self) -> "Cursor":
        '''resets the cursor position to 0.'''
        self._last_pos = self.pos
        self.pos = 0
        return self

    # Makes the position of the cursor to the end of the text
    def to_end(self) -> "Cursor":
        '''Resets the cursor position to the end of the string'''
        self._last_pos = self.pos
        self.pos = len(self._text)
        return self
    
        # Moves the cursor times you give it
    
    # Moves forward a specific amount of times you give it
    def mov(self, times: int) -> "Cursor":
        '''Moves forwards a specific amount of time you give it.'''
        if not isinstance(times, int):
            raise TypeError(f"Expected int, got {type(times).__name__}")
        if times < 0:
            raise ValueError(f"mov only accepts positive integers, got {times}")
        

        self._last_pos = self.pos
        self.pos = min(self.pos + times, len(self._text))
        return self
    
    # Goes back times you give it
    def back(self, times: int) -> "Cursor":
        '''Goes back a specific amount of time you give it.'''
        if not isinstance(times, int):
            raise TypeError(f"Expected int, got {type(times).__name__}")
        if times < 0:
            raise ValueError(f"back only accepts positive integers to subtract, got {times}")
        
        self._last_pos = self.pos
        self.pos = max(self.pos - times, 0)
        return self

    # Goes back until you reach a specific character
    def back_until_char(self, char: str) -> "Cursor":
        '''Goes backwards until any item is a list is found.'''
        self._last_pos = self.pos
        found = self._text.rfind(char, 0, self.pos)
        if found == -1:
            raise ValueError(f"Character '{char}' not found before cursor")
        self.pos = found
        return self

    # Moves to a specific index given to the function
    def mov_to(self, index: int) -> "Cursor":
        '''Moves to a specific location you give it.'''
        if not isinstance(index, int):
            raise TypeError(f"Expected int, got {type(index).__name__}")
        if index > len(self._text):
            raise IndexError("Index out of range")
        if index < 0:
            raise ValueError("mov_to only accepts positive integers.")
        self._last_pos = self.pos
        self.pos = index
        return self
    
    def mov_word(self) -> "Cursor":
        
        self._last_pos = self.pos   
        self.mov_until_any([' ', '\t', '\n'])
        while self.pos < len(self._text) and self._text[self.pos] in [' ', '\t', '\n']:
            self.mov(1)
        
        return self


    '''MODIFICATIONS'''

    # Allows you ro insert a \t (tab) into a specific location
    def tab(self) -> "Cursor":
        return self.__insert_char("\t")

    # This allows you to insert a \n (enter) into a specific location
    def enter(self) -> "Cursor":
        return self.__insert_char("\n")
    
    # Mainly used after select(), allows you to replace a certain text with other text
    def replace_text(self, new_text: str) -> "Cursor":
        '''Replaces the selected text to a new text.'''
        if self.selection is None:
            raise NoSelectionError("Cannot replace: No selection made.")
        start, end = self.selection
        before = self._text[:start]
        after = self._text[end:]
        self._text = f"{before}{new_text}{after}"
        self.pos = start + len(new_text)
        self.selection = None
        return self

    # Allows you to insert text without select
    def insert_text(self, text: str, leave_space: bool = False) -> "Cursor":
        '''Inserts text into the current position, does not leave
        space between old and new text, have to set leave_space = True for that.'''
        pos = self.pos
        if leave_space:
            text = f" {text} "
        before = self._text[:self.pos]
        after = self._text[self.pos:]
        self._text = f"{before}{text}{after}"
        self.pos += len(text)
        self._save_state("insert", pos, text)
        return self
    
    # Deletes seleted text
    def del_text(self) -> "Cursor":
        '''Deletes the selected text.'''
        if self.selection is None:
            raise NoSelectionError("Cannot delete: No selection made.")
        start, end = self.selection
        before = self._text[:start]
        after = self._text[end:]
        deleted_text = self._text[start:end]
        self._text = f"{before}{after}"
        self.selection = None
        self.pos = start
        self._save_state("delete", self.pos, deleted_text)
        return self




    '''SELECTION'''

    # Selects a specific amount from starting point x to ending point y for editing
    def select(self) -> "Cursor":
        '''Function selects the sentence from 
        the last postion you were at to the current position.'''
        start = self._last_pos
        end = self.pos
        self.selection = (min(start, end), max(start, end))
        self._last_pos = self.pos
        return self
    
    #This is useful if you know the exact index values in the string, allows you to selects a specific range of text
    def select_range(self, start: int, end: int) -> "Cursor":
        '''Selects a sentence starting from a start position to end position'''
        self._last_pos = self.pos
        self.selection = (min(start, end), max(start, end))
        return self

    # Selects the full word your on
    def select_word(self) -> "Cursor":
        self._last_pos = self.pos
        
        text = self._text
        pos = self.pos

        for match in re.finditer(r'\b\w+\b', text):
            if match.start() < pos < match.end():
                self.selection = (match.start(), match.end())

        if self.selection is None:
            raise NoSelectionError("Cannot select word: cursor not on a word")

        return self

    # Selects one character you are on
    def select_char(self) -> "Cursor":
        
        self._last_pos = self.pos

        self.mov(2)
        self.back(1)
        self.select()

        return self

    # Selects the full line you're on
    def select_line(self) -> "Cursor":
        text = self._text
        pos = self.pos

        start = text.rfind('\n', 0, pos) + 1
        end = text.find('\n', pos)

        if end == -1:
            end = len(text)

        self.selection = (start, end)
        return self
    

    '''COPY/CUT/PASTE'''
    
    # Copies a selected sentence
    def copy(self) -> "Cursor":
        if self.selection:
            if len(self.clipboard) > MAX_CLIPBOARD:
                self.clipboard.pop()
            self.clipboard.append(self.selected_text)
            return self
        else:
            raise NoSelectionError("Cannot copy: No selection made")
    
    # Cuts a selected section
    def cut(self) -> "Cursor":
        if self.selection:
            if len(self.clipboard) > MAX_CLIPBOARD:
                self.clipboard.pop()    
            self.clipboard.append(self.selected_text)
            self.del_text()
            return self
        else:
            raise NoSelectionError("Cannot cut: No selection made")

    # Pastes the cut/copied section, works FILO
    def paste(self) -> "Cursor":
        if self.clipboard:  
            self.insert_text(self.clipboard.pop())  
        return self


    '''UNDO/REDO'''

    # This undoes the action you just did
    def undo(self) -> "Cursor":
        if not self._history:
            pass
        actions, pos, text = self._history.pop()
        if actions == "insert":
            self._text = self._text[:pos] + self._text[pos+len(text):]
            self.pos = pos
        elif actions == "delete":
            self._text = self._text[:pos] + text + self._text[pos:]
            self.pos = pos
        self._redo_stack.append((actions, pos, text))
        return self
    
    # This redoes the action you just did
    def redo(self) -> "Cursor":
        if not self._redo_stack:
            pass
        action, pos, text = self._redo_stack.pop()
        if action == "insert":
            self._text = self._text[:pos] + text + self._text[pos:]
            self.pos = pos + len(text)
        elif action == "delete":
            self._text = self._text[:pos] + self._text[pos+len(text):]
            self.pos = pos
        self._history.append((action, pos, text))
        return self

    '''PROPERTIES'''

    # Shows the current state of the object
    @property
    def snapshot(self):
        return (self._text, self.pos, self.selection)
    
    # used to show what all text is selected
    @property
    def selected_text(self):
        if self.selection is None:
            return ""
        start, end = self.selection
        return self._text[start:end]

    @property
    def total_chars(self):
        return len(self._text) 

    # Shows the current index
    @property
    def index(self):
        return self.pos
    
    # Shows the fully modified text
    @property
    def return_text(self):
        return self._text

    @property
    def __credits__(self):
        text = '''Credits to Sarvesh E R for this module.'''
        return text