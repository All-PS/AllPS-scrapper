import random
import time

from selenium.common import NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait

from app.config.DriverConfig import DriverConfig
from app.crawler.BaseCrawler import BaseCrawler
from app.dto.SolutionDto import SolutionDto
from app.service.SolutionService import SolutionService


# todo. 직전 문제 set 기억...
class CFSolutionCrawler(BaseCrawler):
    PLATFORM_NAME = "codeforces"
    PLATFORM_URL = "https://codeforces.com/"
    BASE_URL = "https://codeforces.com/problemset/status/page/"
    SET_PAGE = "5"

    def __init__(self, notification, stopEvent):
        self.driver = None
        self.wait = None
        self.notification = notification
        self.solutionService = SolutionService(notification, "C++")
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

                self.saveSolutionsInPage()
                time.sleep(random.uniform(8, 12))

        except Exception as e:
            raise

    def saveSolutionsInPage(self):
        try:
            acceptedRows = self.getAcceptedRows()
            for row in acceptedRows:
                SolutionDto = self.getSolutionDetail(row)
                if SolutionDto:
                    self.solutionService.saveSolution(SolutionDto)

        except Exception as e:
            self.notification.alert(f"[Error] Codeforces Status 페이지를 불러오지 못했습니다. 다시 시도합니다.")

    def getAcceptedRows(self):
        try:
            self.driver.get(self.BASE_URL + self.SET_PAGE)
            self.wait.until(lambda driver: driver.find_elements(By.XPATH, '//tbody/tr'))
            acceptedRows = self.driver.find_elements(By.XPATH, "//tr[.//span[contains(@class, 'verdict-accepted')]]")
        except NoSuchElementException:
            acceptedRows = None
        return acceptedRows

    def getSolutionDetail(self, row):
        code = None
        try:
            code = row.find_element(By.XPATH, './/td[4]/a').text.split()[0]
            isCPP = self.findCPP(row)
            # todo. 추후 getProgrammingLaguage로 변경
            language = 'C++'
            if isCPP:
                solution = self.getSolution(row)
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
            # self.wait.until(lambda driver: driver.find_elements(By.CLASS_NAME, "linenums"))
            time.sleep(3)
            # todo. 팝업 열면 id=linenums div가 생기는데 팝업을 닫으면 해당 div가 사라지지 않음. 따라서 wait 적절하지 않음. 일단 3초 슬립하여 로딩 대기
            lines = self.driver.find_elements(By.CSS_SELECTOR, ".linenums li")
            solution = "\n".join(line.get_attribute("textContent").strip() for line in lines)
            self.driver.find_element(By.CSS_SELECTOR, "a.close").click()
        except NoSuchElementException:
            solution = 'None'
        return solution

    def findCPP(self, row):
        # todo. 추후 getProgrammingLaguage로 변경
        try:
            lang = row.find_element(By.XPATH, './/td[5]').text
            if 'C++' in lang:
                isCPP = True
            else:
                isCPP = False
        except NoSuchElementException:
            isCPP = False
        return isCPP

    def cleanup(self):
        if self.driver:
            self.driver.quit()
