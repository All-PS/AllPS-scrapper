import MySQLdb
import settings

class DatabaseConnection:
    _instance = None

    def __new__(cls):
        if not cls._instance:
            cls._instance = super().__new__(cls)
            cls._instance = MySQLdb.connect(
                **settings.DATABASES
            )
        return cls._instance

    def save_baekjoon(problem):
        db = DatabaseConnection()
        cursor = db.cursor()

        # 이미 해당 값이 존재하는지 확인
        cursor.execute("SELECT code FROM problem WHERE code = %s", (problem.code,))
        exist = cursor.fetchone()

        if exist:
            # 이미 해당 값이 존재하면 업데이트
            update_sql = """
                UPDATE problem
                SET name = %s, tier = %s, url = %s
                WHERE code = %s
            """
            update_params = (problem.name, problem.tier, problem.url, problem.code)
            cursor.execute(update_sql, update_params)
        else:
            # 값이 존재하지 않으면 인서트
            insert_sql = """
                INSERT INTO problem (code, name, tier, url)
                VALUES (%s, %s, %s, %s)
            """
            insert_params = (problem.code, problem.name, problem.tier, problem.url)
            cursor.execute(insert_sql, insert_params)

        db.commit()
        cursor.close()