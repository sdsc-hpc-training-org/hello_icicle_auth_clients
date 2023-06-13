import time
import sys
import os

import pandas as pd
import keyboard
from tabulate import tabulate
from colorama import Fore, Back, Style, init
form = {'ID':None, "Port": None, "Host": None}


class FormHandler:
    up = "\u2191"
    down = "\u2193"
    selection_time_interval = 0.05
    def __init__(self):
        self.time_of_last_input = time.time()
        self.up_reference = None
        self.down_reference = None
        self.position_index = 0
        self.max_position_index = 0
        self.form = None
        self.formatted_form_string = None
        self.form_lines = None
        self.current_field_name = None

    def __select_string_formatter(self, string):
        return f"{Fore.BLACK}{Back.WHITE}{string}{Style.RESET_ALL}"
    
    def move_cursor_up(self, lines):
        sys.stdout.write(f"\033[{lines}A")
        sys.stdout.flush()
    
    def move_cursor_down(self, lines):
        sys.stdout.write(f"\033[{lines}B")
        sys.stdout.flush()
    
    def __stringify_form(self):
        form_present = pd.DataFrame.from_dict(self.form)
        self.formatted_form_string = tabulate(form_present, headers='keys', tablefmt='heavy_grid', showindex=False)
        self.form_lines = len(self.formatted_form_string.split("\n")) - 1

    def __print_form(self):
        self.__stringify_form()
        self.move_cursor_up(self.form_lines)
        print(f"\r{self.formatted_form_string}\r", end="\r")
        self.move_cursor_down(self.form_lines + 2)
    
    def __increment(self, direction):
        if time.time() - self.time_of_last_input >= self.selection_time_interval:
            self.form['Field'][self.position_index] = self.current_field_name
            if direction == "UP":
                self.position_index += 1
            elif direction == "DOWN":
                self.position_index -= 1
            if self.position_index == self.max_position:
                self.position_index = 0
            elif self.position_index == -1:
                self.position_index = self.max_position - 1
            self.current_field_name = self.form['Field'][self.position_index]
            self.form['Field'][self.position_index] = self.__select_string_formatter(self.form['Field'][self.position_index])
            self.__print_form()
            self.time_of_last_input = time.time()

    def form_formatter(self, unformatted_form: dict) -> dict:
        formatted_form = {"Field":[], "Response":[]}
        for name, value in unformatted_form.items():
            formatted_form['Field'].append(name)
            formatted_form['Response'].append(value)
        return formatted_form
    
    def de_format_form(self, formatted_form: dict) -> dict:
        return dict([(name, value) for name, value in zip(formatted_form['Field'], formatted_form['Response'])])
    
    def initiate_form(self, form):
        self.form = self.form_formatter(form)
        self.__stringify_form()
        print("\n" * self.form_lines)
        self.current_field_name = self.form['Field'][self.position_index]
        self.max_position = len(self.form['Field'])
        self.up_reference = keyboard.add_hotkey('down', lambda: self.__increment("UP")) 
        self.down_reference = keyboard.add_hotkey('up', lambda: self.__increment("DOWN"))
        self.__print_form()
        self.handle_input()

    def handle_input(self):
        while True:
            input_value = input(f"\r{self.current_field_name}\r")

#keyboard.remove_hotkey
# while True:
#     pass

# def form_handler(form):
#     field = ""
#     form_present = pd.DataFrame.from_dict(form)
#     print(tabulate(form_present, headers='keys', tablefmt='heavy_grid', showindex=False), end="\r")
        
        


# form_handler(form)

form_handler = FormHandler()
form_handler.initiate_form(form)