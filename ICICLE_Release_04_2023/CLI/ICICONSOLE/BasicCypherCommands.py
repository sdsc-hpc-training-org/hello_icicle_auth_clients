def getAll():
    return "MATCH(n) RETURN n"

def getOne(id):
    return "MATCH(n) WHERE n.id = '" + id + "' RETURN n"

def getOneByType(type):
    return "MATCH(n:" + type + ") RETURN n"

def getONeByName(name):
    return "MATCH(n) WHERE n.name = '" + name + "' RETURN n"