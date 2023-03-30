def getAll():
    return "MATCH(n) RETURN n"

def getAllNames():
    return "MATCH(n) RETURN n.name"

def getOne(id):
    return "MATCH(n) WHERE n.id = '" + id + "' RETURN n"

def getOneByType(type):
    return "MATCH(n:" + type + ") RETURN n"

def getOneByName():
    name = str(input("Enter name: "))
    return "MATCH(n) WHERE n.name = '" + name + "' RETURN n"

def allProperty():
    property = str(input("Enter property: "))
    return "MATCH(n) RETURN n." + property

def allPropertiesForNode():
    id = str(input("Enter id: "))
    return "MATCH(n) WHERE n.id = '" + id + "' RETURN keys(n)"