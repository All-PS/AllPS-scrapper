import random
import time
import re

from selenium.common import NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait

from app.config.DriverConfig import DriverConfig
from app.crawler.BaseCrawler import BaseCrawler
from app.dto.SolutionDto import SolutionDto
from app.service.SolutionService import SolutionService


class CFSolutionCrawler(BaseCrawler):
    PLATFORM_NAME = 2 # "codeforces"
    PLATFORM_URL = "https://codeforces.com/"
    BASE_URL1 = "https://codeforces.com/problemset/status/"
    BASE_URL2 = "/problem/"
    SET_ORDER = "?order=BY_ARRIVED_DESC"

    def __init__(self, notification, stopEvent):
        self.driver = None
        self.wait = None
        self.notification = notification
        self.solutionService = SolutionService(notification, "C++", self.PLATFORM_NAME)
        self.stopEvent = stopEvent

    def cleanup(self):
        if self.driver:
            self.driver.quit()

    def initialize(self):
        self.driver = DriverConfig().getDriver()
        self.wait = WebDriverWait(self.driver, 30)

    def start(self):
        try:
            while True:
                if self.stopEvent.is_set():
                    break
                problemCodes = self.getNoSolutionProblem()
                self.saveSolution(problemCodes)
                time.sleep(random.uniform(8, 12))

        except Exception as e:
            raise

    def getNoSolutionProblem(self):
        try:
            problemCodes = self.solutionService.findProblems()
            newCodes = []
            for i, (id, code) in enumerate(problemCodes):
                if i >= 500:  # 500개 처리
                    break

                match = re.match(r"(\d+)([A-Za-z]+)(\d*)", code)
                if match:
                    contest = match.group(1)
                    ignoreContest = ['1910','1639', '1773', '1578', '1533', '1403', '1297']
                    # 1910 1533 1297 코틀린 전용, 1778 1578 1403 솔루션 조회 불가

                    if contest in ignoreContest:
                        continue

                    problemLetter = match.group(2)
                    problemNum = match.group(3)
                    problemLetter = problemLetter + problemNum
                    # todo. 현재 cpp 언어만 받는데 kotlin 전용 대회 존재로 해당 대회 무시
                    newCode = (id, contest, problemLetter)
                    newCodes.append(newCode)
            return newCodes
        except Exception as e:
            self.notification.alert(f"[Error] DB에서 Solution이 없는 Codeforces Problem을 불러오지 못했습니다. 다시 시도합니다.")
            return None

    def saveSolution(self, problemCodes):
        try:
            for id, contest, problem in problemCodes:
                self.openSolutionPage(contest, problem)
                row = self.findCPPRow()
                if row is None:
                    continue
                SolutionDto = self.getSolutionDetail(contest, problem, row)
                if SolutionDto:
                    self.solutionService.saveSolution(SolutionDto)

        except Exception as e:
            self.notification.alert(f"[Error] Codeforces Status 페이지를 불러오지 못했습니다. 다시 시도합니다.")

    def openSolutionPage(self, contest, problem):
        try:
            self.driver.get(self.BASE_URL1 + contest + self.BASE_URL2 + problem+ self.SET_ORDER)
            self.wait.until(lambda driver: driver.find_elements(By.XPATH, '//tbody/tr'))
        except Exception as e:
            self.notification.alert(f"[Error] Codeforces 문제({contest, problem})의 Solution Page 열기 실패했습니다. 다음 문제로 넘어갑니다.")

    def getSolutionDetail(self,contest, problem, row):
        try:
            # todo. 추후 getProgrammingLaguage로 변경
            language = 'C++'
            solution = self.getSolution(row)
            code = contest + problem
            return SolutionDto(solution, language, code)

        except Exception as e:
            if code:
                self.notification.alert(f"[Error] Codeforces 문제({code})의 Solution을 가져오는데 실패했습니다. 다음 문제로 넘어갑니다.")
            else:
                self.notification.alert(f"[Error] Codeforces Solution을 가져오는데 실패했습니다. 다음 문제로 넘어갑니다.")
            return None

    def getSolution(self, row):
        try:
            row.find_element(By.CLASS_NAME, "view-source").click()
            time.sleep(random.uniform(2, 4))
            self.wait.until(lambda driver: driver.find_elements(By.CLASS_NAME, "linenums"))
            lines = self.driver.find_elements(By.CSS_SELECTOR, ".linenums li")
            solution = "\n".join(line.get_attribute("textContent").strip() for line in lines)
            self.driver.find_element(By.CSS_SELECTOR, "a.close").click()
        except Exception as e:
            solution = 'None'
        return solution

    def findCPPRow(self):
        # todo. 추후 getProgrammingLaguage로 변경
        rows = self.driver.find_elements(By.XPATH, "//tbody/tr[position() > 1]")
        cppRow = None
        try:
            for row in rows:
                lang = row.find_element(By.XPATH, './/td[5]').text
                if 'C++' in lang:
                    cppRow = row
                    break
        except NoSuchElementException:
            cppRow = None
        return cppRow

    def cleanup(self):
        if self.driver:
            self.driver.quit()
