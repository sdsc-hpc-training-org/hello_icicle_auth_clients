1. Consider adding an abstract command class interface thing, or metaclass from which the different commands under the tapis systems can inherit. THis would allow the help generator to iterate over the attributes of the class, instead of explicitly specifying a dict of commands, this could be autogenerated. 
This way the "partial" thing with the decorators could be phased out. This would also make it so the methods dont have to have a connection parameter. Command state can be changed depending on whether the code is running headless or as a client. metaclass checks for doc on the command