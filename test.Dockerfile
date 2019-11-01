FROM python:3.7-slim-buster

RUN pip install pip==19.3.1

COPY /requirements/test.txt /tmp/requirements/test.txt

RUN pip install -r /tmp/requirements/test.txt

COPY /redirect_resolver /code/redirect_resolver
COPY /testing_server /code/testing_server
COPY /tests /tests
ENV PYTHONPATH=/code/

CMD ["pytest", "-v", "/tests"]

