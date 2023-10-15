import random
import re
import time

from selenium.webdriver.common.by import By
from dao.dao import DatabaseConnection
from model.baekjoon_problem import BaekjoonProblem


def baekjoon_scrapper(driver):
    # 페이지 열기
    driver.get('https://www.acmicpc.net/problemset')

    # 전체 페이지 가져오기
    pages_text = driver.find_elements(By.XPATH, '//ul[@class=\'pagination\']/li')[-1].text
    pages = int(pages_text)

    for page in range(1, pages + 1):
        # 페이지 이동
        driver.get('https://www.acmicpc.net/problemset/' + str(page))

        # 문제 리스트 가져오기
        problems = driver.find_elements(By.XPATH, '//tbody/tr')

        for problem in problems:
            # a 태그의 href 속성 가져오기
            link = problem.find_element(By.XPATH, './/td[2]/a').get_attribute('href')

            # 새 탭에서 링크 열기
            driver.execute_script("window.open('', '_blank');")
            driver.switch_to.window(driver.window_handles[-1])
            driver.get(link)

            # 문제 정보 가져오기
            code = re.search(r'/(\d+)$', driver.current_url).group(1)
            name = driver.find_element(By.ID, 'problem_title').text
            url = link
            problem = BaekjoonProblem(code=code, name=name, url=url)

            # 결과 출력
            print(problem.__repr__())
            DatabaseConnection.save_baekjoon(problem)

            # 현재 탭 닫기
            driver.close()

            # 처음 탭으로 전환
            driver.switch_to.window(driver.window_handles[0])

            time.sleep(random.uniform(8,12))