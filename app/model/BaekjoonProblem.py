from app.model.Problem import Problem

class BaekjoonProblem(Problem):

    def __init__(self, code, name, url, updatedAt, tier=None, categories=None):
        super().__init__(code, name, url, updatedAt, tier, self.__toEntity(categories))

    def __toEntity(self, categories):
        return None # Todo. String > CategoryList 변환