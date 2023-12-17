from app.util.SlackBot import SlackBot

def errorLog(service, index1, index2, errMessage):
    with open(f"log/{service}ErrorLog.txt", "w") as file:
        file.write(f"Index1: {index1}, Index2:{index2}, Error: {errMessage}\n")

class ErrorLogger:
    def __init__(self, service, slackAlert='0', index1=None):
        # 초기화 시 서비스명, print/slack 모드 설정
        self.service = service
        self.slackAlert = slackAlert
        self.index1 = index1

    def setIndex1(self, index):
        self.index1 = index

    def getIndex1(self):
        return self.index1

    def logError(self, index2, errMessage):
        # 에러 로그 파일에 write
        with open(f"log/{self.service}ErrorLog.txt", "a") as file:
            if self.index1 is not None:
                file.write(f"Index1: {self.index1}")
            file.write(f"Index2: {index2}, Error: {errMessage}\n")

    def log(self, message):
        # 메세지 출력 terminal print or slack alert
        if self.slackAlert == 0:
            self.printLog(message)
        elif self.slackAlert == 1:
            self.slackAlert(message)

    def printLog(self, message):
        print(f"[{self.service}]: {message}")

    def slackAlert(self, message):
        SlackBot.alert(f"[{self.service}]: {message}")
        pass
