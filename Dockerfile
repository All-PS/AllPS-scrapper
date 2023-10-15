FROM python:3
WORKDIR /usr/src

# 유틸 설치
RUN apt-get -y update
RUN apt install wget
RUN apt install unzip

# 크롬 설치
RUN wget https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb
RUN apt -y install ./google-chrome-stable_current_amd64.deb

# 파이썬 라이브러리 설치
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# PYTHONPATH 환경 변수 설정
ENV PYTHONPATH /usr/src

# 크롤러 복사 & 실행
COPY app ./app
CMD [ "python", "app/main.py" ]