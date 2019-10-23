FROM python:3.7-slim-buster

RUN pip install pip==19.3.1

COPY /requirements/testing-server.txt /tmp/requirements.txt

RUN pip install -r /tmp/requirements.txt

COPY /testing_server /code/testing_server

WORKDIR /code/

ENV PYTHONPATH=/code/
ENTRYPOINT ["python", "/code/testing_server/app.py"]
