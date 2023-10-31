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


def crawlSolvedac():
    driver = ChromeDriver()
    wait = WebDriverWait(driver, 10)
    # SlackBot.alert("dev Solvedac 크롤링이 시작되었습니다.")
    pages = getPageNumber(driver)
    crawlPages(driver, pages, wait)


def crawlPages(driver, pages, wait):
    for page in range(1, pages + 1):
        openTagListPage(driver, page)
        tags = getTags(driver, wait)
        for idx, tag in enumerate(tags, 1):
            try:  # 태그 진입
                taglink = getTagLink(tag, wait)
                openNewTab(driver, taglink)
            except Exception as e:
                print("Exception: ", e)
            problems = getTags(driver, wait)
            # 해당 태그 진입하여 문제 정보 따오기까지 완완완
            # todo 문제 번호, 티어 정보 DB화 작업......... 슬랙 알람 tag명 구현..?

        # 실제 태그명 아님..
        SlackBot.alert(f"Solved {tag} 태그의 크롤링이 완료되었습니다.")


def getPageNumber(driver):
    driver.get('https://solved.ac/problems/tags')
    pages_text = driver.find_elements(By.XPATH, '//div[@class=\'css-18lc7iz\']/a')[-1].text
    pages = int(pages_text)
    return pages


def getTags(driver, wait):
    wait.until(EC.presence_of_element_located((By.XPATH, '//tbody/tr')))
    tags = driver.find_elements(By.XPATH, '//tbody/tr')
    return tags


def openTagListPage(driver, page):
    driver.get('https://solved.ac/problems/tags?page=' + str(page))


def openTagSetPage(driver, tag):
    driver.get('https://solved.ac/problems/tags/' + str(tag))


def openNewTab(driver, link):
    driver.execute_script("window.open('', '_blank');")
    driver.switch_to.window(driver.window_handles[-1])
    driver.get(link)


def closeNewTab(driver):
    driver.close()
    driver.switch_to.window(driver.window_handles[0])


def getTagLink(tag, wait):
    wait.until(EC.presence_of_element_located((By.XPATH, './/td[2]/a')))
    link = tag.find_element(By.XPATH, './/td[2]/a').get_attribute('href')
    return link
