class TaskCallback:
    def __init__(self, logger, task):
        self.logger, self.task = logger, task
        print("DOING THE INIT")

    def __call__(self):
        print("CALLED")


x = TaskCallback(1,2)
x()