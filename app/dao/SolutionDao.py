class SolutionDao:

    def __init__(self, dbConnection):
        self.dbConnection = dbConnection
        self.dbConnection.autocommit = False

    def get(self, platform_id):
        try:
            with self.dbConnection.cursor() as cursor:
                noSolutionProblems = self._checkNoSolutionProblem(cursor, platform_id)
            return noSolutionProblems
        except Exception as e:
            raise e
            return None

    def save(self, solution, programmingLanguage, problemCode):
        try:
            with self.dbConnection.cursor() as cursor:
                # programmingLanguageId = self._insertProgrammingLanguage(cursor, programmingLanguage)
                problemId = self._checkProblemExists(cursor, problemCode)
                if problemId:
                    problemId = self._insertSolution(cursor, solution.code, 1, problemId[0])
        except Exception as e:
            raise e

    def _checkProgrammingLanguageExists(self, cursor, programmingLanguageName):
        check_query = "SELECT id FROM programming_language WHERE name = %s"
        cursor.execute(check_query, programmingLanguageName)
        return cursor.fetchone()

    def _checkProblemExists(self, cursor, problemCode):
        check_query = "SELECT id FROM problem WHERE code = %s"
        # todo. 플랫폼 별 code 동일 문제 존재,,, platformID도 select 조건에 추가 필요
        # check_query = "SELECT id FROM problem WHERE code = %s AND platform_id = %s"
        cursor.execute(check_query, (problemCode,))
        return cursor.fetchone()

    def _checkNoSolutionProblem(self, cursor, platform_id):
        check_query = "SELECT p.id, p.code FROM problem p LEFT JOIN solution s ON p.id = s.problem_id WHERE p.platform_id = %s AND s.id IS NULL"
        cursor.execute(check_query, (platform_id,))
        return cursor.fetchall()

    def _checkSolutionExists(self, cursor, problemId):
        check_query = "SELECT id FROM solution WHERE problem_id = %s"
        cursor.execute(check_query, (problemId,))
        return cursor.fetchone()

    def _insertProgrammingLanguage(self, cursor, programmingLanguageName):
        existing_platform = self._checkProgrammingLanguageExists(cursor, programmingLanguageName)
        if existing_platform:
            return existing_platform[0]

        platform_query = "INSERT INTO programming_language (name) VALUES (%s)"
        cursor.execute(platform_query, (programmingLanguageName))
        return cursor.lastrowid

    def _insertSolution(self, cursor, solution, languageId, problemId):
        # existing_solution = self._checkSolutionExists(cursor, problemId)
        # if existing_solution:
        #     problemId = existing_solution[0]
        #     # self._updateProblem(cursor, asdf)
        #
        # else:
        insert_query = ("INSERT INTO solution (code, programming_language_id, problem_id) VALUES (%s, %s, %s)")
        cursor.execute(insert_query, (solution, languageId, problemId,))
        problemId = cursor.lastrowid

            # todo. 프로그래밍 언어 추가...?
            # for platformCategoryId in platformCategoryIds:
            #     problem_category_query = "INSERT INTO problem_platform_category (problem_id, platform_category_id) VALUES (%s, %s)"
            #     cursor.execute(problem_category_query, (problemId, platformCategoryId))
        return problemId
