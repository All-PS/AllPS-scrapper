import random
import time
from datetime import datetime

import pytz
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from app.dao.ProblemDao import ProblemDao
from app.model.BaekjoonProblem import BaekjoonProblem
from app.provider.BaekjoonProvider import tags
from app.util.ChromeDriver import ChromeDriver
from app.util.DatabaseConnection import DatabaseConnection
from app.util.SlackBot import SlackBot


def crawlSolvedac():
    driver = ChromeDriver()
    wait = WebDriverWait(driver, 10)
    SlackBot.alert("Solvedac 크롤링이 시작되었습니다.")
    crawlTags(driver, wait)


def crawlTags(driver, wait):
    for cId in range(3, len(tags)):
        category = tags[cId][0]
        pageUrls = tags[cId][1:]
        # 태그 별 문제 정보 크롤링
        for url in pageUrls:
            openPage(driver, url)
            crawlPages(driver, wait, url, cId + 1)

        SlackBot.alert(f"Solvedac {category} 태그의 크롤링이 완료되었습니다.")


def crawlPages(driver, wait, url, cId):
    # 태그 내 페이지 수
    pages = getPageNumber(driver)
    for page in range(1, pages + 1):
        openProblemSetPage(driver, url, page)
        DatabaseConnection.startTransaction()

        getProblemData(driver, wait, cId)

        # 5페이지마다 트랜젝션 커밋
        if page % 5 == 0:
            DatabaseConnection.commitTransaction()
            DatabaseConnection.startTransaction()

        time.sleep(random.uniform(4, 6))


def getPageNumber(driver):
    pages_text = driver.find_elements(By.XPATH, '//div[@class=\'css-18lc7iz\']/a')[-1].text
    pages = int(pages_text)
    return pages


def openPage(driver, link):
    driver.get(link)


def openProblemSetPage(driver, link, page):
    driver.get(link + "?page=" + str(page))


def getProblemData(driver, wait, cId):
    wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, 'tr.css-1ojb0xa')))
    rows = driver.find_elements(By.CSS_SELECTOR, 'tr.css-1ojb0xa')
    rows.pop(0)

    for row in rows:
        # 각 컬럼의 데이터 추출
        key = row.find_element(By.CSS_SELECTOR, 'span.css-1raije9 a span').text
        name = row.find_element(By.CSS_SELECTOR, 'span.css-1oteowz').text
        url = "https://www.acmicpc.net/problem/" + key
        now = datetime.now(pytz.timezone('Asia/Seoul')).strftime('%Y-%m-%d %H:%M:%S')
        tier = row.find_element(By.CSS_SELECTOR, 'img.css-1vnxcg0').get_attribute('alt')

        problem = BaekjoonProblem(key=key, name=name, url=url, updatedAt=now, platformId=1, difficultyId=tier,
                                  categoryId=cId)
        ProblemDao.save(problem)

# def getProblems(driver, wait):
#     wait.until(EC.presence_of_element_located((By.XPATH, '//tbody/tr')))
#     tags = driver.find_elements(By.XPATH, '//tbody/tr')
#     return tags
#
#
# def openNewTab(driver, link):
#     driver.execute_script("window.open('', '_blank');")
#     driver.switch_to.window(driver.window_handles[-1])
#     driver.get(link)
#
#
# def closeNewTab(driver):
#     driver.close()
#     driver.switch_to.window(driver.window_handles[0])
