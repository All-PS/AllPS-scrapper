from app.util.DatabaseConnection import DatabaseConnection


class ProblemDao:

    def save(problem):
        # 커서 가져오기
        cursor = DatabaseConnection().cursor()

        # 이미 해당 값이 존재하는지 확인
        select_sql = "SELECT code FROM problem WHERE code = %s"
        select_params = (problem.code,)
        problemId = cursor.execute(select_sql, select_params)
        exist = cursor.fetchone()

        if exist:
            # 이미 해당 값이 존재하면 업데이트
            update_sql = """
                UPDATE problem
                SET name = %s, tier = %s, categoryid = %s, url = %s, updated_at = %s
                WHERE code = %s
            """
            update_params = (
            problem.name, problem.tier, problem.categoryid, problem.url, problem.updatedAt, problem.code)
            cursor.execute(update_sql, update_params)
        else:
            # 값이 존재하지 않으면 인서트
            insert_sql = """
                INSERT INTO problem (code, name, tier, categoryid, url, updated_at)
                VALUES (%s, %s, %s, %s, %s, %s)
            """
            insert_params = (
            problem.code, problem.name, problem.tier, problem.categoryid, problem.url, problem.updatedAt)
            cursor.execute(insert_sql, insert_params)

        return problemId
