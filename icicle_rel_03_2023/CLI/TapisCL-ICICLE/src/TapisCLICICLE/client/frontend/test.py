import time
import sys
import os
import typing
import signal
import asyncio
import threading
import string


import pydantic
import blessed
import pandas as pd
import keyboard
from tabulate import tabulate
from colorama import Fore, Back, Style, init
form = {'ID':None, "Port": None, "Host": None}

logpath = r"C:\Users\ahuma\Desktop\log.txt"

def log(data):
    with open(logpath, 'a') as f:
        f.write(str(data))

term = blessed.Terminal()

ACCEPTED_KEYS = string.ascii_lowercase + string.ascii_uppercase + string.digits 


class Form(pydantic.BaseModel):
    Fields: list[str]
    Values: list | None = []
    index: int = 0
    previous_index: tuple[int, str] = (0, '')
    max_index: int = 0

    def __init__(self, form: dict[str, typing.Any]):
        Fields = list(form.keys())
        Values = list(form.values())
        if not Fields:
            raise AttributeError("Must supply fields for the form")
        for index, value in enumerate(Values):
            if not value:
                Values[index] = ''
        super().__init__(Fields=Fields, Values=Values, index=0, max_index=len(Fields), previous_index = (0, Fields[0]))
        self.Fields[0] = self.__select_string_formatter(Fields[0])

    def __select_string_formatter(self, string):
        return f"{Fore.BLACK}{Back.WHITE}{string}{Style.RESET_ALL}"
    
    def increment(self, direction: typing.Literal['UP', 'DOWN']):
        previous_index, name = self.previous_index
        if direction == "UP":
            self.index += 1
        elif direction == "DOWN":
            self.index -= 1
        if self.index == self.max_index:
            self.index = 0
        elif self.index == -1:
            self.index = self.max_index - 1
        self.Fields[previous_index] = name
        self.previous_index = (self.index, self.Fields[self.index])
        self.Fields[self.index] = self.__select_string_formatter(self.Fields[self.index])

    def set_value(self, value):
        self.Values[self.index] = value

    def current_value(self):
        return self.Values[self.index]

    def __str__(self):
        form_present = pd.DataFrame.from_dict({'Field':self.Fields, 'Value':self.Values})
        formatted_form_string = tabulate(form_present, headers='keys', tablefmt='rounded_grid', showindex=False, maxcolwidths=50)
        return formatted_form_string

    def dict(self) -> dict:
        return dict([(name, value) for name, value in zip(self.Fields, self.Values)])
    

class FormHandler:
    refresh_rate = 0.01666
    def __init__(self):
        self.form: Form = None
        self.input_location_minimum = (0, 0)
        self.input_location_maximum = (0, 0)
        self.location = (0, 0)
        self.size = (0, 0)

    def shift_cursor(self, direction: int = 1):
        x, y = self.location
        if (x, y) in (self.input_location_maximum, self.input_location_minimum):
            return ""
        x += 1*direction
        if x < 0:
            x = term.width
            y -= 1
        elif x > term.width:
            x = 0
            y += 1
        self.location = (x, y)
        log(f"LOCATION: {self.location}")
        return term.move_xy(x, y)

    
    def register_form(self, form):
        self.form = form

    def print_form(self):
        print(f"{term.home}{str(self.form)}\n{form.Fields[form.index]}: ", end='', flush=True)
        self.input_location_minimum = term.get_location()
        print(f"{form.Values[form.index]}{term.clear_eos()}", end='', flush=True)
        self.input_location_maximum = term.get_location()
        self.location = self.input_location_maximum
        log(f"MAXIMUM LOCATION{self.input_location_maximum}")

    def window_change_event(self):
        if term.width != self.size[0] or term.height != self.size[1]:
            self.size = (term.width, term.height)
            self.print_form()      

    def accept_input(self):
        keystroke = term.inkey(timeout=self.refresh_rate)
        if not keystroke:
            pass
        elif keystroke.is_sequence:
            if keystroke.name == 'KEY_UP':
                self.down()
            elif keystroke.name == 'KEY_DOWN':
                self.up()
            elif keystroke.name == 'KEY_BACKSPACE':
                self.backspace()
            elif keystroke.name == "KEY_ENTER":
                self.up()
            elif keystroke.name == "KEY_LEFT":
                print(f"{self.shift_cursor(-1)}", flush=True, end='')
            elif keystroke.name == "KEY_RIGHT":
                print(f"{self.shift_cursor()}", flush=True, end='')
        elif keystroke:
            self.form.set_value(self.form.current_value() + keystroke)
            print(f"{self.shift_cursor()}{keystroke}", flush=True, end='')

    def backspace(self):
        if True:
            #self.form.set_value(self.form.current_value()[:-1])
            print(f" {self.shift_cursor(-1)}{self.shift_cursor()}", end='', flush=True)

    def up(self):
        self.form.increment('UP')
        self.print_form()

    def down(self):
        self.form.increment('DOWN')
        self.print_form()

    def handle_input(self):
        old_hook = sys.stdin.readline
        sys.stdin.readline = lambda: old_hook().rstrip()
        with term.fullscreen(), term.cbreak():
            self.print_form()
            self.size = (term.width, term.height)
            while True:
                self.window_change_event()
                self.accept_input()

# form_handler(form)


form = Form(form)
form.set_value("asldkfl;kasdf;lkjasdlkfkjasl;kkdjflkajfgl;kjadfl;kgjla;skkjgfl;sdjfgljals;fjlasdjfl;jadsljdaflgkjasl;dfjlasdjdflajsd;lfjasl;dfjlasdfjlkasdjflkasjdf;;lksajdfl;kjsdfa")

form_handler = FormHandler()
form_handler.register_form(form)
form_handler.handle_input()
