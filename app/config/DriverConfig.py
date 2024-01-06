from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager


class DriverConfig:
    def __init__(self):
        options = webdriver.ChromeOptions()
        # options.add_argument("--headless")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--disable-gpu")

        service = Service(executable_path=ChromeDriverManager().install())
        self.driver = webdriver.Chrome(service=service, options=options)

    def getDriver(self):
        return self.driver
