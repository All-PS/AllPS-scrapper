from datetime import datetime


class ProblemDao:

    def __init__(self, dbConnection):
        self.dbConnection = dbConnection
        self.dbConnection.autocommit = False

    def save(self, problem, platform, platformCategories, platformDifficulty):
        try:
            with self.dbConnection.cursor() as cursor:
                platformId = self._insertPlatform(cursor, platform)
                platformCategoryIds = self._insertPlatformCategories(cursor, platformCategories, platformId)
                platformDifficultyId = self._insertPlatformDifficulty(cursor, platformDifficulty, platformId)
                problemId = self._insertProblem(cursor, problem, platformId, platformCategoryIds, platformDifficultyId)
        except Exception as e:
            raise e

    def _checkPlatformExists(self, cursor, platform):
        check_query = "SELECT id FROM platform WHERE name = %s"
        cursor.execute(check_query, (platform.name,))
        return cursor.fetchone()

    def _checkPlatformCategoryExists(self, cursor, platformCategory, platformId):
        check_query = "SELECT id FROM platform_category WHERE name = %s AND platform_id = %s"
        cursor.execute(check_query, (platformCategory.name, platformId))
        return cursor.fetchone()

    def _checkPlatformDifficultyExists(self, cursor, platformDifficulty, platformId):
        check_query = "SELECT id FROM platform_difficulty WHERE name = %s AND platform_id = %s"
        cursor.execute(check_query, (platformDifficulty.name, platformId))
        return cursor.fetchone()

    def _checkProblemExists(self, cursor, problem, platformId):
        check_query = "SELECT id FROM problem WHERE code = %s AND platform_id = %s"
        cursor.execute(check_query, (problem.code, platformId))
        return cursor.fetchone()

    def _insertPlatform(self, cursor, platform):
        existing_platform = self._checkPlatformExists(cursor, platform)
        if existing_platform:
            return existing_platform[0]

        platform_query = "INSERT INTO platform (name, url) VALUES (%s, %s)"
        cursor.execute(platform_query, (platform.name, platform.url))
        return cursor.lastrowid

    def _insertPlatformCategories(self, cursor, platformCategories, platformId):
        platformCategoryIds = []
        for platformCategory in platformCategories:
            existing_category = self._checkPlatformCategoryExists(cursor, platformCategory, platformId)

            if existing_category:
                platformCategoryId = existing_category[0]

            else:
                category_query = "INSERT INTO platform_category (name, platform_id) VALUES (%s, %s)"
                cursor.execute(category_query, (platformCategory.name, platformId))
                platformCategoryId = cursor.lastrowid

            platformCategoryIds.append(platformCategoryId)
        return platformCategoryIds

    def _insertPlatformDifficulty(self, cursor, platformDifficulty, platformId):
        existing_difficulty = self._checkPlatformDifficultyExists(cursor, platformDifficulty, platformId)
        if existing_difficulty:
            return existing_difficulty[0]

        difficulty_query = "INSERT INTO platform_difficulty (name, platform_id) VALUES (%s, %s)"
        cursor.execute(difficulty_query, (platformDifficulty.name, platformId))
        return cursor.lastrowid

    def _insertProblem(self, cursor, problem, platformId, platformCategoryIds, platformDifficultyId):
        existing_problem = self._checkProblemExists(cursor, problem, platformId)
        if existing_problem:
            problemId = existing_problem[0]
            self._updateProblem(cursor, problem, problemId, platformCategoryIds, platformDifficultyId)

        else:
            insert_query = "INSERT INTO problem (code, name, url, solved_count, platform_id, platform_difficulty_id, difficulty_id) VALUES (%s, %s, %s, %s, %s, %s, %s)"
            cursor.execute(insert_query, (problem.code, problem.name, problem.url, problem.solvedCount, platformId, platformDifficultyId, 1))
            problemId = cursor.lastrowid

            for platformCategoryId in platformCategoryIds:
                problem_category_query = "INSERT INTO problem_platform_category (problem_id, platform_category_id) VALUES (%s, %s)"
                cursor.execute(problem_category_query, (problemId, platformCategoryId))
        return problemId

    def _updateProblem(self, cursor, problem, problemId, platformCategoryIds, platformDifficultyId):
        update_query = "UPDATE problem SET name = %s, url = %s, updated_at = %s, solved_count = %s, platform_difficulty_id = %s, difficulty_id = %s WHERE id = %s"
        cursor.execute(update_query, (problem.name, problem.url, datetime.now(), problem.solvedCount, platformDifficultyId, 1, problemId))

        if platformCategoryIds:
            delete_query = "DELETE FROM problem_platform_category WHERE problem_id = %s AND platform_category_id NOT IN %s"
            cursor.execute(delete_query, (problemId, tuple(platformCategoryIds)))
        else:
            delete_all_query = "DELETE FROM problem_platform_category WHERE problem_id = %s"
            cursor.execute(delete_all_query, (problemId,))

        for platformCategoryId in platformCategoryIds:
            check_query = "SELECT 1 FROM problem_platform_category WHERE problem_id = %s AND platform_category_id = %s"
            cursor.execute(check_query, (problemId, platformCategoryId))
            if not cursor.fetchone():
                insert_query = "INSERT INTO problem_platform_category (problem_id, platform_category_id) VALUES (%s, %s)"
                cursor.execute(insert_query, (problemId, platformCategoryId))