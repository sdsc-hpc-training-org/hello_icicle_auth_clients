from colorama import Fore, Back, Style, init

# Initialize colorama
init()

# Example text
text = "Hello, world!"

# Print highlighted text
print(f"{Fore.RED}{Style.BRIGHT}{text}{Style.RESET_ALL}")  # Red and bright
x = f"{Fore.BLACK}{Back.WHITE}{text}{Style.RESET_ALL}"  # Green background and dim
print(f"{Fore.YELLOW}{Back.BLUE}{Style.BRIGHT}{text}{Style.RESET_ALL}")  # Yellow text, blue background, and bright

print(x)
