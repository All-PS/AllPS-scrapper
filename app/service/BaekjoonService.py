import random
import re
import time
from datetime import datetime

import pytz
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from app.dao.ProblemDao import ProblemDao
from app.model.BaekjoonProblem import BaekjoonProblem
from app.util.ChromeDriver import ChromeDriver
from app.util.DatabaseConnection import DatabaseConnection
from app.util.SlackBot import SlackBot

def getPageNumber(driver):
    driver.get('https://www.acmicpc.net/problemset')
    pages_text = driver.find_elements(By.XPATH, '//ul[@class=\'pagination\']/li')[-1].text
    pages = int(pages_text)
    return pages

def openProblemSetPage(driver, page):
    driver.get('https://www.acmicpc.net/problemset/' + str(page))

def openNewTab(driver, link):
    driver.execute_script("window.open('', '_blank');")
    driver.switch_to.window(driver.window_handles[-1])
    driver.get(link)

def closeNewTab(driver):
    driver.close()
    driver.switch_to.window(driver.window_handles[0])

def getProblemData(driver, link, wait):
    code = re.search(r'/(\d+)$', driver.current_url).group(1)
    wait.until(EC.presence_of_element_located((By.ID, 'problem_title')))
    name = driver.find_element(By.ID, 'problem_title').text
    url = link
    tier = None  # Todo. Tier 가져오기
    categories = None  # Todo. Categories 가져오기
    now = datetime.now(pytz.timezone('Asia/Seoul')).strftime('%Y-%m-%d %H:%M:%S')

    problem = BaekjoonProblem(code=code, name=name, url=url, tier=tier, categories=categories, updatedAt=now)
    ProblemDao.save(problem)

def crawlProblems():
    driver = ChromeDriver()
    wait = WebDriverWait(driver, 10)
    SlackBot.alert("백준 크롤링이 시작되었습니다.")

    pages = getPageNumber(driver)

    for page in range(1, pages + 1):
        openProblemSetPage(driver, page)

        wait.until(EC.presence_of_element_located((By.XPATH, '//tbody/tr')))
        problems = driver.find_elements(By.XPATH, '//tbody/tr')

        DatabaseConnection.startTransaction()

        for idx, problem in enumerate(problems, 1):
            wait.until(EC.presence_of_element_located((By.XPATH, './/td[2]/a')))
            link = problem.find_element(By.XPATH, './/td[2]/a').get_attribute('href')

            openNewTab(driver, link)
            getProblemData(driver, link, wait)
            closeNewTab(driver)

            # 매 10개의 문제마다 트랜잭션 커밋
            if idx % 10 == 0:
                DatabaseConnection.commitTransaction()
                DatabaseConnection.startTransaction()

        # 남은 트랜잭션 커밋
        DatabaseConnection.commitTransaction()

        time.sleep(random.uniform(8, 12))
        SlackBot.alert(f"백준 {page} 페이지의 크롤링이 완료되었습니다.")
