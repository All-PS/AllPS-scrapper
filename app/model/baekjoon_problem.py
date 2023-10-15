class BaekjoonProblem:
    def __init__(self, code, name, url, tier=None, categories=None):
        self.code = code
        self.name = name
        self.tier = tier
        self.url = url
        self.categories = categories

    def __repr__(self):
        return f"Problem(code='{self.code}', name='{self.name}', tier='{self.tier}', url='{self.url}', categories={self.categories})"