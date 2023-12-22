import random
import time

from selenium.common import NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait

from app.config.DriverConfig import DriverConfig
from app.crawler.BaseCrawler import BaseCrawler
from app.dto.ProblemDto import ProblemDto
from app.service.ProblemService import ProblemService


class CodeforcesCrawler(BaseCrawler):
    PLATFORM_NAME = "codeforces"
    PLATFORM_URL = "https://codeforces.com/"
    BASE_URL = "https://codeforces.com/problemset/page/"

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
        self.driver.get(self.BASE_URL + '1')
        self.wait.until(lambda driver: driver.find_element(By.XPATH, '//span[@class=\'page-index\']/a'))
        totalPages = int(self.driver.find_elements(By.XPATH, '//span[@class=\'page-index\']/a')[-1].text)
        return totalPages

    def saveProblemsInPage(self, page):
        try:
            self.driver.get(self.BASE_URL + str(page))
            self.wait.until(lambda driver: driver.find_elements(By.XPATH, '//tbody/tr'))

            rows = self.driver.find_elements(By.XPATH, '//tbody/tr')[1:-1]

            for row in rows:
                problemDto = self.getProblemDetail(row)
                if problemDto:
                    self.problemService.saveProblem(problemDto)


        except Exception as e:
            self.notification.alert(f"[Error] Codeforces 문제 페이지({page})를 불러오지 못했습니다. 다음 페이지로 넘어갑니다.")

    def getProblemDetail(self, row):
        code = None
        try:
            code = row.find_element(By.XPATH, './/td[1]/a').text.strip()
            url = row.find_element(By.XPATH, './/td[1]/a').get_attribute('href')
            name = row.find_element(By.XPATH, './/td[2]/div[1]/a').text
            solvedCount = self.getSolvedCount(row)
            platformDifficulty = self.getPlatformDifficulty(row)
            platformCategories = self.getPlatformCategories(row)
            return ProblemDto(code, name, url, platformDifficulty, solvedCount, platformCategories)

        except Exception as e:
            if code:
                self.notification.alert(f"[Error] Codeforces 문제({code})의 정보를 가져오는데 실패했습니다. 다음 문제로 넘어갑니다.")
            else:
                self.notification.alert(f"[Error] Codeforces 문제의 정보를 가져오는데 실패했습니다. 다음 문제로 넘어갑니다.")
            return None

    def getSolvedCount(self, row):
        try:
            solvedCount = row.find_element(By.XPATH, './/td[5]/a').text.strip().split('x')[1].strip()
        except NoSuchElementException:
            solvedCount = -1
        return solvedCount

    def getPlatformDifficulty(self, row):
        try:
            platformDifficulty = row.find_element(By.XPATH, './/td[4]/span').text
        except NoSuchElementException:
            platformDifficulty = 'Unrated'
        return platformDifficulty

    def getPlatformCategories(self, row):
        try:
            tags_elements = row.find_elements(By.XPATH, './/td[2]/div[2]/a')
            platformCategories = [tag.text.strip() for tag in tags_elements]
        except NoSuchElementException:
            platformCategories = []
        return platformCategories

    def cleanup(self):
        if self.driver:
            self.driver.quit()
