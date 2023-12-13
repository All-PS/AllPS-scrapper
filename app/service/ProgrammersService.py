import random
import re
import time
from datetime import datetime

import pytz
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from app.dao.ProblemDao import ProblemDao
from app.model.ProgrammersProblem import ProgrammersProblem
from app.util.ChromeDriver import ChromeDriver
from app.util.DatabaseConnection import DatabaseConnection
from app.util.SlackBot import SlackBot
from app.util.ErrorLogger import errorLog

service = "programmers"


def crawlProgrammers():
    driver = ChromeDriver()
    wait = WebDriverWait(driver, 10)
    SlackBot.alert("Programmers 크롤링이 시작되었습니다.")
    crawlProblems(driver, wait)


def crawlProblems(driver, wait):
    page = 1
    while True:
        openProblemSetPage(driver, page)
        DatabaseConnection.startTransaction()

        getProblemData(driver, wait, page)

        # 5페이지마다 트랜젝션 커밋
        if page % 5 == 0:
            DatabaseConnection.commitTransaction()
            DatabaseConnection.startTransaction()

        time.sleep(random.uniform(8, 12))

        # 페이지 증가
        page += 1


def openPage(driver, link):
    try:
        driver.get(link)
    except Exception as e:
        SlackBot.alert(f"페이지 열기 실패: {link} / Exception: {e}\n")
        errorLog(service, link, "NULL", e)


def openProblemSetPage(driver, page):
    link = "https://school.programmers.co.kr/learn/challenges?order=recent"

    try:
        openPage(driver, link + "&page=" + str(page))

        current_url = driver.current_url

        # 현재 URL에 page 값이 포함되어 있고, 그 값이 현재 페이지 값보다 작다면 page 값을 1로 초기화합니다.
        if "&page=" in current_url and int(current_url.split("&page=")[1]) < page:
            page = 1
    except Exception as e:
        SlackBot.alert(f"페이지 열기 실패: {link} page= {page} / Exception: {e}\n")
        errorLog(service, link, page, e)


def getProblemData(driver, wait, page):
    try:
        wait.until(EC.presence_of_element_located((By.XPATH, '//tbody/tr')))
        rows = driver.find_elements(By.XPATH, '//tbody/tr')
    except Exception as e:
        SlackBot.alert(f"{page}페이지 크롤링 실패 / Exception: {e}\n")
        errorLog(service, page, page, e)
        return

    for row in rows:
        try:
            #Todo
            #difficultyId,categoryId
            name_element = row.find_element(By.CSS_SELECTOR, 'td.title a')
            name = name_element.text

            url = name_element.get_attribute('href')

            now = datetime.now(pytz.timezone('Asia/Seoul')).strftime('%Y-%m-%d %H:%M:%S')

            # 문제 번호 추출 - URL에서 마지막 숫자 부분을 코드로 사용
            code_match = re.search(r'/(\d+)$', url)
            code = code_match.group(1) if code_match else None

            # 프로그래머스 레벨 추출
            level_element = row.find_element(By.CSS_SELECTOR, 'td.level span')
            level = level_element.text.split()[-1]

            # Finished Count 추출
            solved_count_element = row.find_element(By.CSS_SELECTOR, 'td.finished-count')
            solvedCount_text = solved_count_element.text.replace('명', '').replace(',', '')
            solvedCount = int(solvedCount_text)

            problem = ProgrammersProblem(code=code, name=name, url=url, updatedAt=now, platformId=2, difficultyId=31,
                                         categoryId=0, solvedCount=solvedCount, realDifficulty=level)
            ProblemDao.save(problem)
        except Exception as e:
            SlackBot.alert(f"{page}페이지 데이터 처리 중 오류 / Exception: {e}\n")
            errorLog(service, page, page, e)
            continue
