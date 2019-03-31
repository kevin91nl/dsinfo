FROM python:3.7.2-alpine3.9

COPY requirements.txt /requirements.txt

RUN pip install -r /requirements.txt

RUN python -m nltk.downloader stopwords

RUN mkdir /app/

WORKDIR /app/

COPY . /app/

ENTRYPOINT ["python", "run.py", "--path", "/data/"]