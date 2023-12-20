from app.config.DatabaseConfig import DatabaseConfig
from app.dao.ProblemDao import ProblemDao
from app.entity.Platform import Platform
from app.entity.PlatformCategory import PlatformCategory
from app.entity.PlatformDifficulty import PlatformDifficulty
from app.entity.Problem import Problem
from app.service.BaseService import BaseService


class CodeforcesService(BaseService):
    PLATFORM_NAME = "codeforces"
    PLATFORM_URL = "https://codeforces.com/"

    def __init__(self, notification):
        databaseConfig = DatabaseConfig()
        self.dbConnection = databaseConfig.getConnection()
        self.problemDao = ProblemDao(self.dbConnection)
        self.notification = notification

    def saveProblem(self, codeforcesProblem):
        platform = Platform(self.PLATFORM_NAME, self.PLATFORM_URL)
        platformDifficulty = PlatformDifficulty(codeforcesProblem.platformDifficulty)
        problem = Problem(codeforcesProblem.code, codeforcesProblem.name, codeforcesProblem.url, codeforcesProblem.solvedCount)
        platformCategories = []
        for platformCategoryName in codeforcesProblem.platformCategories:
            platformCategories.append(PlatformCategory(platformCategoryName))

        try:
            self.dbConnection.begin()
            self.problemDao.save(problem, platform, platformCategories, platformDifficulty)
            self.dbConnection.commit()
        except Exception as e:
            self.notification.alert(f"[Error] 데이터베이스에 문제를 저장하는데 오류가 발생했습니다. ({platform.name} {problem.code})")
            self.dbConnection.rollback()
            raise e
