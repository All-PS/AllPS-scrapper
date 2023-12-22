from app.config.DatabaseConfig import DatabaseConfig
from app.dao.ProblemDao import ProblemDao
from app.entity.Platform import Platform
from app.entity.PlatformCategory import PlatformCategory
from app.entity.PlatformDifficulty import PlatformDifficulty
from app.entity.Problem import Problem


class ProblemService():
    def __init__(self, notification, platformName, platformUrl):
        databaseConfig = DatabaseConfig()
        self.dbConnection = databaseConfig.getConnection()
        self.problemDao = ProblemDao(self.dbConnection)
        self.notification = notification
        self.platformName = platformName
        self.platformUrl = platformUrl

    def saveProblem(self, problemDto):
        platform = Platform(self.platformName, self.platformUrl)
        platformDifficulty = PlatformDifficulty(problemDto.platformDifficulty)
        problem = Problem(problemDto.code, problemDto.name, problemDto.url, problemDto.solvedCount)
        platformCategories = []
        for platformCategoryName in problemDto.platformCategories:
            platformCategories.append(PlatformCategory(platformCategoryName))

        try:
            self.dbConnection.begin()
            self.problemDao.save(problem, platform, platformCategories, platformDifficulty)
            self.dbConnection.commit()
        except Exception as e:
            self.notification.alert(f"[Error] 데이터베이스에 문제를 저장하는데 오류가 발생했습니다. ({platform.name} {problem.code})")
            self.dbConnection.rollback()
            raise e
