try: 
    raise OSError('silliness')
except Exception as e:
    print(type(e))