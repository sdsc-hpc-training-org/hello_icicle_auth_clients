try:
    from . import cli
except:
    import cli


client = cli.CLI('127.0.0.1', 3000)
client.main()