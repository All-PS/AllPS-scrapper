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
from app.settings import BAEKJOON_ID, BAEKJOON_PW
from app.util.ChromeDriver import ChromeDriver
from app.util.DatabaseConnection import DatabaseConnection
from app.util.SlackBot import SlackBot


def baekjoonLogin(driver, wait):
    driver.get('https://www.acmicpc.net/login')
    # 아이디 및 비밀번호 입력 필드 찾기
    wait.until(EC.presence_of_element_located((By.NAME, "login_user_id")))
    wait.until(EC.presence_of_element_located((By.NAME, "login_password")))
    username_elem = driver.find_element(By.NAME, "login_user_id")
    password_elem = driver.find_element(By.NAME, "login_password")

    # 아이디 및 비밀번호 입력
    username_elem.send_keys(BAEKJOON_ID)  # 여기에 사용자 이름을 입력해주세요.
    password_elem.send_keys(BAEKJOON_PW)  # 여기에 비밀번호를 입력해주세요.
    # 로그인 버튼 클릭
    wait.until(EC.presence_of_element_located((By.ID, "submit_button")))
    login_button = driver.find_element(By.ID, "submit_button")
    login_button.click()
    time.sleep(5)


def crawlBaekjoon():
    driver = ChromeDriver()
    wait = WebDriverWait(driver, 10)
    SlackBot.alert("백준 크롤링이 시작되었습니다.")
    pages = getPageNumber(driver)
    baekjoonLogin(driver, wait)
    crawlPages(driver, pages, wait)


def crawlPages(driver, pages, wait):
    for page in range(1, pages + 1):
        openProblemSetPage(driver, page)
        problems = getProblems(driver, wait)
        DatabaseConnection.startTransaction()

        crawlProblems(driver, problems, wait)

        # 남은 트랜잭션 커밋
        DatabaseConnection.commitTransaction()

        SlackBot.alert(f"백준 {page} 페이지의 크롤링이 완료되었습니다.")


def crawlProblems(driver, problems, wait):
    for idx, problem in enumerate(problems, 1):
        try:
            link = getProblemLink(problem, wait)
            openNewTab(driver, link)
        except Exception as e:
            print(idx, "번 크롤링 실패\n Exception: ", e)
            continue

        try:
            getProblemData(driver, link, wait)
        except Exception as e:
            print(idx, "번 크롤링 실패\n Exception: ", e)
        finally:
            closeNewTab(driver)
            # 매 10개의 문제마다 트랜잭션 커밋
            if idx % 10 == 0:
                DatabaseConnection.commitTransaction()
                DatabaseConnection.startTransaction()
            time.sleep(random.uniform(8, 12))


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


def getProblemLink(problem, wait):
    wait.until(EC.presence_of_element_located((By.XPATH, './/td[2]/a')))
    link = problem.find_element(By.XPATH, './/td[2]/a').get_attribute('href')
    return link


def getProblems(driver, wait):
    wait.until(EC.presence_of_element_located((By.XPATH, '//tbody/tr')))
    problems = driver.find_elements(By.XPATH, '//tbody/tr')
    return problems
