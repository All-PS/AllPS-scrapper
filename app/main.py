from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from app.scrapper.baekjoon_scrapper import baekjoon_scrapper

def main():
    # 웹 드라이버 초기화
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    service = Service(executable_path=ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)

    # 플랫폼별 크롤링
    while True:
        baekjoon_scrapper(driver)

    # 셀레니움 웹 드라이버 종료
    driver.quit()

if __name__ == "__main__":
    main()
