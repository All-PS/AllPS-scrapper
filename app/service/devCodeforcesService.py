import random
import time
from datetime import datetime

import pytz
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from app.dao.ProblemDao import ProblemDao
from app.model.CodeforcesProblem import CodeforcesProblem
from app.util.ChromeDriver import ChromeDriver
from app.util.DatabaseConnection import DatabaseConnection
from app.util.ErrorLogger import errorLog

service = "codeforces"


def crawlCodeforces():
    driver = ChromeDriver()
    wait = WebDriverWait(driver, 10)
    print("dev/ Codeforces 크롤링이 시작되었습니다.\n")
    crawlPages(driver, wait)


def crawlPages(driver, wait):
    openProblemSetPage(driver, 1)
    pages = getPageNumber(driver, wait)
    for page in range(1, pages + 1):
        openProblemSetPage(driver, page)
        DatabaseConnection.startTransaction()

        getProblemData(driver, wait, page)

        # 5페이지마다 트랜젝션 커밋
        if page % 5 == 0 or page == pages:
            DatabaseConnection.commitTransaction()
            DatabaseConnection.startTransaction()

        time.sleep(random.uniform(8, 12))


def getPageNumber(driver, wait):
    wait.until(EC.presence_of_element_located((By.XPATH, '//span[@class=\'page-index\']/a')))
    pages_text = driver.find_elements(By.XPATH, '//span[@class=\'page-index\']/a')[-1].text
    pages = int(pages_text)
    return pages


def openPage(driver, link):
    try:
        driver.get(link)
    except Exception as e:
        print(f"페이지 열기 실패: {link} / Exception: {e}\n")
        errorLog(service, link, "NULL", e)


def openProblemSetPage(driver, page):
    try:
        driver.get("https://codeforces.com/problemset/page/" + str(page))
    except Exception as e:
        print(f"페이지 열기 실패: page= {page} / Exception: {e}\n")
        errorLog(service, page, 0, e)


def getProblemData(driver, wait, page):
    try:
        wait.until(EC.presence_of_element_located((By.XPATH, '//tbody/tr')))
        rows = driver.find_elements(By.XPATH, '//tbody/tr')
        rows.pop(0)
    except Exception as e:
        # SlackBot.alert(cId, page, "페이지 크롤링 실패\n Exception: ", e)
        print(f"{page}페이지 크롤링 실패 / Exception: {e}\n")
        errorLog(service, page, 0, e)
        return

    for row in rows:
        try:
            print(row.text)
            td1 = row.find_element(By.XPATH, './/td[1]/a')
            code = td1.text.strip()
            url = td1.get_attribute('href')
            name = row.find_element(By.XPATH, './/td[2]/div[1]/a').text.strip()
            now = datetime.now(pytz.timezone('Asia/Seoul')).strftime('%Y-%m-%d %H:%M:%S')

            tags_elements = row.find_elements(By.XPATH, './/td[2]/div[2]/a')
            category = ', '.join([tag.text.strip() for tag in tags_elements])

            solvedCount = row.find_element(By.XPATH, './/td[5]/a').text.strip().split('x')[1].strip()
            difficulty = row.find_element(By.XPATH, './/td[4]/span').text.strip()

            problem = CodeforcesProblem(code=code, name=name, url=url, updatedAt=now, platformId=3, difficultyId=31,
                                        categoryId=0, solvedCount=solvedCount, realDifficulty=difficulty, )
            ProblemDao.save(problem)
        except Exception as e:
            errorLog(service, page, 0, e)
            continue
