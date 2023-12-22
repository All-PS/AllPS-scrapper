import random
import re
import time
from urllib.parse import urlparse, parse_qs

from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait

from app.config.DriverConfig import DriverConfig
from app.crawler.BaseCrawler import BaseCrawler
from app.dto.ProblemDto import ProblemDto
from app.service.ProblemService import ProblemService


class ProgrammersCrawler(BaseCrawler):
    PLATFORM_NAME = "programmers"
    PLATFORM_URL = "https://programmers.co.kr/"
    BASE_URL = "https://school.programmers.co.kr/learn/challenges?order=acceptance_desc"

    def __init__(self, notification, stopEvent):
        self.driver = None
        self.wait = None
        self.notification = notification
        self.problemService = ProblemService(notification, self.PLATFORM_NAME, self.PLATFORM_URL)
        self.stopEvent = stopEvent

    def cleanup(self):
        if self.driver:
            self.driver.quit()

    def initialize(self):
        self.driver = DriverConfig().getDriver()
        self.wait = WebDriverWait(self.driver, 30)

    def start(self):
        try:
            totalPages = self.getTotalPages()

            for page in range(1, totalPages + 1):
                if self.stopEvent.is_set():
                    break

                self.saveProblemsInPage(page)
                time.sleep(random.uniform(8, 12))

        except Exception as e:
            raise

    def getTotalPages(self):
        self.driver.get(self.BASE_URL)
        self.wait.until(lambda driver: driver.find_element(By.XPATH,
                                                           "//button[@class='PaginationNavstyle__ArrowEnd-sc-1ye3koq-2 fWEGtA last' and @aria-label='마지막 페이지']"))
        self.driver.find_element(By.XPATH,
                                 "//button[@class='PaginationNavstyle__ArrowEnd-sc-1ye3koq-2 fWEGtA last' and @aria-label='마지막 페이지']").click()
        return int(parse_qs(urlparse(self.driver.current_url).query).get('page', [None])[0])

    def saveProblemsInPage(self, page):
        try:
            self.driver.get(self.BASE_URL + "&page=" + str(page))
            self.wait.until(lambda driver: driver.find_elements(By.XPATH, '//tbody/tr'))

            rows = self.driver.find_elements(By.XPATH, '//tbody/tr')

            for row in rows:
                problemDto = self.getProblemDetail(row)
                if problemDto:
                    self.problemService.saveProblem(problemDto)

        except Exception as e:
            self.notification.alert(f"[Error] Programmers 문제 페이지({page})를 불러오지 못했습니다. 다음 페이지로 넘어갑니다.")

    def getProblemDetail(self, row):
        code = None
        try:
            name = row.find_element(By.CSS_SELECTOR, 'td.title a').text
            url = row.find_element(By.CSS_SELECTOR, 'td.title a').get_attribute('href')
            code = re.search(r'/(\d+)$', url).group(1)
            solvedCount = int(
                row.find_element(By.CSS_SELECTOR, 'td.finished-count').text.replace('명', '').replace(',', ''))
            platformDifficulty = row.find_element(By.CSS_SELECTOR, 'td.level span').text
            return ProblemDto(code, name, url, platformDifficulty, solvedCount)

        except Exception as e:
            if code:
                self.notification.alert(f"[Error] Programmers 문제({code})의 정보를 가져오는데 실패했습니다. 다음 문제로 넘어갑니다.")
            else:
                self.notification.alert(f"[Error] Programmers 문제의 정보를 가져오는데 실패했습니다. 다음 문제로 넘어갑니다.")
            return None
