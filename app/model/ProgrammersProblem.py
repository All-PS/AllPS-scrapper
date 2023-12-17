from app.model.Problem import Problem
# from app.d

class ProgrammersProblem(Problem):

    def __init__(self, code, name, url, updatedAt, difficultyId, platformId, categoryId, solvedCount, realDifficulty):
        super().__init__(code, name, url, updatedAt, difficultyId, platformId, categoryId,
                         solvedCount, realDifficulty)

