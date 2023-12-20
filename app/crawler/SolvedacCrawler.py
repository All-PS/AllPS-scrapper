import time

from bs4 import BeautifulSoup
from selenium.common import NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait

from app.config.DriverConfig import DriverConfig
from app.crawler.BaseCrawler import BaseCrawler
from app.dto.SolvedacProblem import SolvedacProblem
from app.service.SolvedacService import SolvedacService


class SolvedacCrawler(BaseCrawler):
    BASE_URL = "https://solved.ac"

    def __init__(self, notification, stopEvent):
        self.driver = None
        self.wait = None
        self.notification = notification
        self.solvedacService = SolvedacService(notification)
        self.stopEvent = stopEvent

    def cleanup(self):
        if self.driver:
            self.driver.quit()

    def initialize(self):
        self.driver = DriverConfig().getDriver()
        self.wait = WebDriverWait(self.driver, 30)

    def start(self):
        try:
            levelPages, levels = self.openStartPage()

            for levelPage, level in zip(levelPages, levels):
                if self.stopEvent.is_set():
                    break

                self.processLevelPage(levelPage, level)

        except Exception as e:
            raise

    def openStartPage(self):
        self.driver.get(self.BASE_URL + '/problems/level')
        self.wait.until(lambda driver: driver.find_element(By.TAG_NAME, 'body'))

        soup = BeautifulSoup(self.driver.page_source, 'html.parser')
        tbody = soup.find('tbody', class_='css-1d9xc1d')
        levelLinks = tbody.find_all('a', href=True)[2::2]

        levelPages = []
        levels = []

        for levelLink in levelLinks:
            levelPages.append(self.BASE_URL + levelLink['href'])
            levels.append(levelLink.get_text().strip())

        return levelPages, levels

    def processLevelPage(self, levelPage, level):
        try:
            problemPages = self.openLevelPage(levelPage)

            for problemPage in problemPages:
                self.saveProblemsInPage(problemPage, level)

        except Exception as e:
            self.notification.alert(f"[Error] Solvedac 난이도 페이지({level})를 불러오지 못했습니다. 다음 난이도로 넘어갑니다.")

    def openLevelPage(self, levelPage):
        self.driver.get(levelPage)
        self.wait.until(lambda driver: driver.find_element(By.XPATH, '//div[@class=\'css-18lc7iz\']/a'))

        soup = BeautifulSoup(self.driver.page_source, 'html.parser')
        pageLinks = soup.select('div.css-18lc7iz > a')
        totalPages = max([int(link.get_text()) for link in pageLinks if 'page=' in link['href']])
        problemPages = [f"{levelPage}?page={pageNumber}" for pageNumber in range(1, totalPages + 1)]
        return problemPages

    def saveProblemsInPage(self, problemPage, level):
        try:
            self.driver.get(problemPage)
            self.wait.until(lambda driver: driver.find_elements(By.CSS_SELECTOR, "tr.css-1ojb0xa"))

            rows = self.driver.find_elements(By.CSS_SELECTOR, "tr.css-1ojb0xa")[1:]

            for index, row in enumerate(rows):
                self.clickButtonToOpenCategories(row)
                solvedacProblem = self.getProblemDetail(index, level)

                if solvedacProblem:
                    self.solvedacService.saveProblem(solvedacProblem)

        except Exception as e:
            self.notification.alert(f"[Error] Solvedac 문제 페이지({problemPage})를 불러오지 못했습니다. 다음 페이지로 넘어갑니다.")

    def clickButtonToOpenCategories(self, row):
        button = row.find_element(By.CSS_SELECTOR, "button.css-gv0s7n")
        self.driver.execute_script("arguments[0].click();", button)
        time.sleep(0.5)

    def getProblemDetail(self, index, level):
        code = None
        try:
            row = self.driver.find_elements(By.CSS_SELECTOR, "tr.css-1ojb0xa")[1:][index]
            code = row.find_element(By.CSS_SELECTOR, "a.css-q9j30p > span").text
            name = row.find_element(By.CSS_SELECTOR, "span.__Latex__").text
            url = "https://www.acmicpc.net/problem/" + code
            solvedCount = row.find_element(By.CSS_SELECTOR, "div.css-1ujcjo0").text.replace(",", "")
            platformDifficulty = level
            platformCategories = self.getPlatformCategories(row)
            return SolvedacProblem(code, name, url, solvedCount, platformDifficulty, platformCategories)

        except Exception as e:
            if code:
                self.notification.alert(f"[Error] Solvedac 문제({code})의 상세정보를 불러오지 못했습니다. 다음 문제로 넘어갑니다.")
            else:
                self.notification.alert(f"[Error] Solvedac 문제의 정보를 가져오는데 실패했습니다. 다음 문제로 넘어갑니다.")
            return None

    def getPlatformCategories(self, row):
        try:
            platformCategoryLinks = row.find_element(By.CSS_SELECTOR, "div.css-1m19b4j").find_elements(By.CSS_SELECTOR,
                                                                                                       "a.css-18la3yb")
            platformCategories = [link.text for link in platformCategoryLinks]
        except NoSuchElementException:
            platformCategories = []
        return platformCategories
