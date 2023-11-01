from app.model.Problem import Problem


class BaekjoonProblem(Problem):

    def __init__(self, code, name, tier, categoryid, url, updatedAt):
        super().__init__(code, name, tier, categoryid, url, updatedAt)
        # super().__init__(code, name, url, updatedAt, tier, self.__toEntity(category))

    def __toEntity(self, category):
        return None  # Todo. String > CategoryList 변환
