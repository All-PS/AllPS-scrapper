from app.model.Problem import Problem
from app.provider.BaekjoonProvider import tiers


# from app.d

class BaekjoonProblem(Problem):

    def __init__(self, code, name, url, updatedAt, difficultyId, platformId, categoryId, solvedCount, realDifficulty):
        super().__init__(code, name, url, updatedAt, self.__toEntity(difficultyId), platformId, categoryId,
                         solvedCount, realDifficulty)

    def __toEntity(self, tier_string):
        for tier_id, tier_name in tiers:
            if tier_name.lower() == tier_string.lower():
                return tier_id
        return None  # 티어를 찾지 못한 경우
