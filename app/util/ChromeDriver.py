import subprocess
import time

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager


class ChromeDriver:
    _instance = None

    def __new__(cls):
        if not cls._instance:
            # Chrome 디버깅 모드로 실행
            chrome_process = subprocess.Popen(
                ["/usr/bin/google-chrome", "--remote-debugging-port=9222", "--headless", "--disable-gpu",
                 "--no-sandbox"])
            time.sleep(5)
            options = webdriver.ChromeOptions()
            options.add_experimental_option("debuggerAddress", "127.0.0.1:9222")
            service = Service(executable_path=ChromeDriverManager().install())
            cls._instance = webdriver.Chrome(service=service, options=options)
        return cls._instance
