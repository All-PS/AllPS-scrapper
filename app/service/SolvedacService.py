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
    # BaekjoonProvider 파일 내 tags List

    for id in range(len(tags)):
        # for tag in tags:
        category = tags[id][0]
        pageUrls = tags[id][1:]
        # 태그 별 문제 정보 크롤링
        for url in pageUrls:
            openPage(driver, url)
            crawlPages(driver, wait, category, url, id + 1)


def crawlPages(driver, wait, category, url, id):
    # 태그 내 페이지 수
    pages = getPageNumber(driver)
    for page in range(1, pages + 1):
        openProblemSetPage(driver, url, page)
        # problems = getProblems(driver, wait)
        DatabaseConnection.startTransaction()

        getProblemData(driver, wait, id)

        # 5페이지마다 트랜젝션 커밋
        if page % 5 == 0:
            DatabaseConnection.commitTransaction()
            DatabaseConnection.startTransaction()

        time.sleep(random.uniform(5, 8))
    SlackBot.alert(f"Solvedac {category} 태그의 크롤링이 완료되었습니다.")


def getPageNumber(driver):
    pages_text = driver.find_elements(By.XPATH, '//div[@class=\'css-18lc7iz\']/a')[-1].text
    pages = int(pages_text)
    return pages


def getProblems(driver, wait):
    wait.until(EC.presence_of_element_located((By.XPATH, '//tbody/tr')))
    tags = driver.find_elements(By.XPATH, '//tbody/tr')
    return tags


def openPage(driver, link):
    driver.get(link)


def openProblemSetPage(driver, link, page):
    driver.get(link + "?page=" + str(page))


def openNewTab(driver, link):
    driver.execute_script("window.open('', '_blank');")
    driver.switch_to.window(driver.window_handles[-1])
    driver.get(link)


def closeNewTab(driver):
    driver.close()
    driver.switch_to.window(driver.window_handles[0])


def getProblemData(driver, wait, id):
    # HTML 요소 선택
    wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, 'tr.css-1ojb0xa')))
    rows = driver.find_elements(By.CSS_SELECTOR, 'tr.css-1ojb0xa')
    rows.pop(0)

    for row in rows:
        # 각 컬럼의 데이터 추출
        code = row.find_element(By.CSS_SELECTOR, 'span.css-1raije9 a span').text
        name = row.find_element(By.CSS_SELECTOR, 'span.css-1oteowz').text
        tier = row.find_element(By.CSS_SELECTOR, 'img.css-1vnxcg0').get_attribute('alt')
        url = "https://www.acmicpc.net/problem/" + code
        now = datetime.now(pytz.timezone('Asia/Seoul')).strftime('%Y-%m-%d %H:%M:%S')

        problem = BaekjoonProblem(code=code, name=name, tier=tier, categoryid=id, url=url, updatedAt=now)
        ProblemDao.save(problem)
