import os


__location__ = os.path.realpath(
    os.path.join(os.getcwd(), os.path.dirname(__file__)))


directory = os.listdir(__location__)
if "test.txt" not in directory:
    print("AHHHH")
    f = open(f"{__location__}\\test.txt", "w")
    f.close()

os.system(f"notepad {__location__}\\test.txt")

print("hehe")