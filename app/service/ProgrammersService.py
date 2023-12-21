from app.config.DatabaseConfig import DatabaseConfig
from app.dao.ProblemDao import ProblemDao
from app.entity.Platform import Platform
from app.entity.PlatformDifficulty import PlatformDifficulty
from app.entity.Problem import Problem
from app.service.BaseService import BaseService


class ProgrammersService(BaseService):
    PLATFORM_NAME = "programmers"
    PLATFORM_URL = "https://programmers.co.kr/"

    def __init__(self, notification):
        databaseConfig = DatabaseConfig()
        self.dbConnection = databaseConfig.getConnection()
        self.problemDao = ProblemDao(self.dbConnection)
        self.notification = notification

    def saveProblem(self, programmersProblem):
        platform = Platform(self.PLATFORM_NAME, self.PLATFORM_URL)
        platformDifficulty = PlatformDifficulty(programmersProblem.platformDifficulty)
        problem = Problem(programmersProblem.code, programmersProblem.name, programmersProblem.url, programmersProblem.solvedCount)
        platformCategories = []

        try:
            self.dbConnection.begin()
            self.problemDao.save(problem, platform, platformCategories, platformDifficulty)
            self.dbConnection.commit()
        except Exception as e:
            self.notification.alert(f"[Error] 데이터베이스에 문제를 저장하는데 오류가 발생했습니다. ({platform.name} {problem.code})")
            self.dbConnection.rollback()
            raise e
