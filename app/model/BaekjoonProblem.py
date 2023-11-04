from app.model.Problem import Problem
from app.provider.BaekjoonProvider import tiers


# from app.d

class BaekjoonProblem(Problem):

    def __init__(self, key, name, url, updatedAt, difficultyId, platformId, categoryId):
        super().__init__(key, name, url, updatedAt, self.__toEntity(difficultyId), platformId, categoryId)

    # todo platform 리스트 작성 & 반환 구현

    def __toEntity(self, tier_string):
        for tier_id, tier_name in tiers:
            if tier_name.lower() == tier_string.lower():
                return tier_id
        return None  # 티어를 찾지 못한 경우
