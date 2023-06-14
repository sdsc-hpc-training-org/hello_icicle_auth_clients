import blessed

term = blessed.Terminal()

with term.fullscreen(), term.cbreak():
    val = ''
    while True:
        val += term.inkey()
        print(val)