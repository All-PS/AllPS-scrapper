from app.util.DatabaseConnection import DatabaseConnection


class ProblemDao:

    # @staticmethod
    def save(problem):
        # 커서 가져오기
        cursor = DatabaseConnection().cursor()

        # 이미 해당 값이 존재하는지 확인
        select_sql = "SELECT * FROM problem JOIN problem_category ON problem.id=problem_category.problem_id WHERE problem.code = %s AND problem_category.category_id = %s"
        select_params = (problem.code, problem.categoryId)
        problemCode = cursor.execute(select_sql, select_params)
        exist = cursor.fetchone()

        if exist:
            # 이미 해당 값이 존재하면 업데이트
            update_sql = """
                UPDATE problem
                SET name = %s, url = %s, updated_at = %s, difficulty_id = %s, platform_id = %s, solved_count = %s
                WHERE code = %s
            """
            update_params = (
                problem.name, problem.url, problem.updatedAt, problem.difficultyId, problem.platformId,
                problem.solved_count, problem.code,)
            cursor.execute(update_sql, update_params)
            # DB에서 문제의 ID
            problemId = exist[0]

        else:
            # 값이 존재하지 않으면 인서트
            insert_sql = """
                INSERT INTO problem (code, name, url, updated_at, difficulty_id, platform_id, solved_count)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """
            insert_params = (
                problem.code, problem.name, problem.url, problem.updatedAt, problem.difficultyId, problem.platformId,
                problem.solved_count,)
            cursor.execute(insert_sql, insert_params)
            problemId = cursor.lastrowid

            # problem_category에 삽입
            if problemId and problem.categoryId:
                insert_category_sql = """
                INSERT IGNORE INTO problem_category (problem_id, category_id)
                VALUES (%s, %s)
                """
                cursor.execute(insert_category_sql, (problemId, problem.categoryId), )

        # 변경 사항을 커밋
        DatabaseConnection().commit()
        return problemCode
