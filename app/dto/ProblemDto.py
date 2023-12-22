class ProblemDto:

    def __init__(self, code, name, url, platformDifficulty, solvedCount=-1, platformCategories=None):
        if platformCategories is None:
            platformCategories = []
        self.code = code
        self.name = name
        self.url = url
        self.solvedCount = solvedCount
        self.platformDifficulty = platformDifficulty
        self.platformCategories = platformCategories
