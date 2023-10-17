class Category:
    def __init__(self, name):
        self.name = name

    @classmethod
    def of(name):
        return Category(name)