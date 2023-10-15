from selenium import webdriver
from scrapper.baekjoon_scrapper import baekjoon_scrapper

def main():
    # 웹 드라이버 초기화
    driver = webdriver.Chrome()

    # 플랫폼별 크롤링
    while True:
        baekjoon_scrapper(driver)

    # 셀레니움 웹 드라이버 종료
    driver.quit()

if __name__ == "__main__":
    main()
