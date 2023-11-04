from app.service.BaekjoonService import crawlBaekjoon
from app.service.SolvedacService import crawlSolvedac

from app.util.ChromeDriver import ChromeDriver


def main():
    # 플랫폼별 크롤링
    while True:
        # crawlBaekjoon()
        crawlSolvedac()

    # DB 연결 끊기
    DatabaseConnection.close()

    # 셀레니움 웹 드라이버 종료
    ChromeDriver().quit()


if __name__ == "__main__":
    main()
