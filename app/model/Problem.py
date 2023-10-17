class Problem:

    def __init__(self, code, name, url, updatedAt, tier=None, categories=None):
        self.code = code
        self.name = name
        self.tier = tier
        self.url = url
        self.categories = categories
        self.updatedAt = updatedAt
