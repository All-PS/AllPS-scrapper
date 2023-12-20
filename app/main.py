import threading
from concurrent.futures import ThreadPoolExecutor

from app.crawler.CodeforcesCrawler import CodeforcesCrawler
from app.crawler.ProgrammersCrawler import ProgrammersCrawler
from app.crawler.SolvedacCrawler import SolvedacCrawler
from app.notification.ConsoleNotification import ConsoleNotification
from app.notification.SlackNotification import SlackNotification


def runCrawler(crawler, notification, crawlerName, stopEvent):
    notification.alert(f"[Notice] {crawlerName} 크롤링이 시작되었습니다.")
    while not stopEvent.is_set():
        try:
            crawler.initialize()
            crawler.start()
            notification.alert(f"[Notice] {crawlerName} 크롤링 작업이 완료되었습니다. 처음부터 재시작합니다.")
        except Exception as e:
            notification.alert(f"[Error] {crawlerName} 크롤링 중 오류가 발생했습니다. 처음부터 재시작합니다.")
        finally:
            crawler.cleanup()
        if stopEvent.is_set():
            break

def main():
    stopEvent = threading.Event()

    notification = SlackNotification()
    # notification = ConsoleNotification()

    solvedacCrawler = SolvedacCrawler(notification, stopEvent)
    codeforcesCrawler = CodeforcesCrawler(notification, stopEvent)
    programmersCrawler = ProgrammersCrawler(notification, stopEvent)

    with ThreadPoolExecutor(max_workers=3) as executor:
        executor.submit(runCrawler, solvedacCrawler, notification, "Solvedac", stopEvent)
        executor.submit(runCrawler, codeforcesCrawler, notification, "Codeforces", stopEvent)
        executor.submit(runCrawler, programmersCrawler, notification, "Programmers", stopEvent)

if __name__ == "__main__":
    main()

