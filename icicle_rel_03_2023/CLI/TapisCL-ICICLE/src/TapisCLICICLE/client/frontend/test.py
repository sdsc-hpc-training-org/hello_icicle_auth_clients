import time
import tableprint
form = {"name":"", "age":""}


def stringify(dictionary):
    stringified = str()
    for name, item in dictionary.items():
        stringified += f"{name}: {item}\n"
    return stringified


def form_handler(form):
    field = ""
    while field != "submit":
        tableprint.table(list(form.items()), headers=['Field', 'Response'])
        field = input("Field: ")


form_handler(form)