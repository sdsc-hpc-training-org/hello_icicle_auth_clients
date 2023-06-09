import argparse


parser = argparse.ArgumentParser()

# Multiple positional arguments with nargs='?'
parser.add_argument('command')
parser.add_argument('arg1', nargs='*', default='default1')

print(parser.parse_args(['1','2', '3']))