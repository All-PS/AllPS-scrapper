from app.model.Problem import Problem


class CodeforcesProblem(Problem):

    def __init__(self, code, name, url, updatedAt, difficultyId, platformId, categoryId, solvedCount, realDifficulty):
        super().__init__(code, name, url, updatedAt, difficultyId, platformId, categoryId,
                         solvedCount, realDifficulty)

    # def __toEntity(self, category_string): self.__toEntity(categoryId)
