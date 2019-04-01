FROM python:3.7.2-alpine3.9

COPY requirements.txt /requirements.txt

RUN pip3 install -r /requirements.txt

RUN python3 -m nltk.downloader stopwords

RUN mkdir /app/

WORKDIR /app/

COPY . /app/

ENTRYPOINT ["python3", "run.py", "--path", "/data/"]