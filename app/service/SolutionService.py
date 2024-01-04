from app.config.DatabaseConfig import DatabaseConfig
from app.dao.SolutionDao import SolutionDao
from app.entity.Problem import Problem
from app.entity.ProgrammingLanguage import ProgrammingLanguage
from app.entity.Solution import Solution


class SolutionService():
    def __init__(self, notification, progLangName):
        databaseConfig = DatabaseConfig()
        self.dbConnection = databaseConfig.getConnection()
        self.solutionDao = SolutionDao(self.dbConnection)
        self.notification = notification
        self.progLangName = progLangName

    def saveSolution(self, solutionDto):
        programmingLanguage = ProgrammingLanguage(self.progLangName)
        solution = Solution(solutionDto.solution)
        # platformCategories = []
        # for platformCategoryName in solutionDto.platformCategories:
        #     platformCategories.append(PlatformCategory(platformCategoryName))

        try:
            self.dbConnection.begin()
            self.solutionDao.save(solution, programmingLanguage, solutionDto.problemCode)
            self.dbConnection.commit()
        except Exception as e:
            self.notification.alert(f"[Error] 데이터베이스에 솔루션을 저장하는데 오류가 발생했습니다. ()")
            self.dbConnection.rollback()
            raise e
