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
from app.util.ErrorLogger import ErrorLogger

slackAlert = 0  # (dev)터미널 print 0 / (main)Slackbot 사용 시 1
logger = ErrorLogger("SolvedAC", slackAlert)


def crawlSolvedac():
    driver = ChromeDriver()
    wait = WebDriverWait(driver, 10)
    logger.log("Solvedac 크롤링이 시작되었습니다.")
    crawlTags(driver, wait)


def crawlTags(driver, wait):
    for cId in range(0, len(tags)):
        category = tags[cId][0]
        pageUrls = tags[cId][1:]
        # 태그 별 문제 정보 크롤링
        for url in pageUrls:
            openPage(driver, url)
            logger.setIndex1(category + url.split('/')[-1])
            crawlPages(driver, wait, url)

        logger.log(f"Solvedac {category} 태그의 크롤링이 완료되었습니다.")


def crawlPages(driver, wait, url):
    # 태그 내 페이지 수
    pages = getPageNumber(driver, wait)
    for page in range(0, pages + 1):
        openProblemSetPage(driver, url, page)
        DatabaseConnection.startTransaction()

        getProblemData(driver, wait, page)

        # 5페이지마다 트랜젝션 커밋
        if page % 5 == 0 or page == pages:
            DatabaseConnection.commitTransaction()
            DatabaseConnection.startTransaction()

        time.sleep(random.uniform(8, 12))


def getPageNumber(driver, wait):
    wait.until(EC.presence_of_element_located((By.XPATH, '//div[@class=\'css-18lc7iz\']/a')))
    pages_text = driver.find_elements(By.XPATH, '//div[@class=\'css-18lc7iz\']/a')[-1].text
    pages = int(pages_text)
    return pages


def openPage(driver, link):
    try:
        driver.get(link)
    except Exception as e:
        logger.log(f"페이지 열기 실패: {link} / Exception: {e}\n")
        logger.logError(link, e)


def openProblemSetPage(driver, link, page):
    try:
        driver.get(link + "?page=" + str(page))
    except Exception as e:
        logger.log(f"페이지 열기 실패: {link} page= {page} / Exception: {e}\n")
        logger.logError(link + "?page=" + str(page), e)


def getProblemData(driver, wait, page):
    try:
        wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, 'tr.css-1ojb0xa')))
        rows = driver.find_elements(By.CSS_SELECTOR, 'tr.css-1ojb0xa')
        rows.pop(0)
    except Exception as e:
        logger.log(f"{logger.getIndex1()}카테고리 {page}페이지 크롤링 실패 / Exception: {e}\n")
        logger.logError(page, e)
    else:
        for row in rows:
            try:
                code = row.find_element(By.CSS_SELECTOR, 'span.css-1raije9 a span').text
                name = row.find_element(By.CSS_SELECTOR, 'span.css-1oteowz').text
                url = "https://www.acmicpc.net/problem/" + code
                now = datetime.now(pytz.timezone('Asia/Seoul')).strftime('%Y-%m-%d %H:%M:%S')
                tier = row.find_element(By.CSS_SELECTOR, 'img.css-1vnxcg0').get_attribute('alt')
                solvedCount = int(row.find_element(By.CSS_SELECTOR, 'div.css-1ujcjo0').text.replace(",", ""))

                problem = BaekjoonProblem(code=code, name=name, url=url, updatedAt=now, platformId=1, difficultyId=tier,
                                          categoryId=cId, solvedCount=solvedCount, realDifficulty=tier, )
                ProblemDao.save(problem)
            except Exception as e:
                logger.log(f"{logger.getIndex1()}카테고리 {page}페이지 문제 데이터 처리 중 오류 / Exception: {e}\n")
                logger.logError(page, e)
                continue
