class Category:
    def __init__(self, name, id):
        self.name = name
        self.id = id

    @classmethod
    def of(name):
        return Category(name)
