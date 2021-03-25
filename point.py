class Point:

    x = None
    y = None

    def __init__(self, x=0, y=0):
        self.x = x
        self.y = y

    def set(self, x, y):
        self.x = x
        self.y = y

    def get(self):
        return self.x, self.y

    def __str__(self):
        return str(self.x) + "," + str(self.y)
