FROM redirect-resolver

COPY /requirements/ /tmp/requirements

RUN pip install -r /tmp/requirements/test.txt

COPY /tests /tests
COPY /testing_server /code/testing_server

ENTRYPOINT [""]

CMD ["pytest", "-v", "/tests"]

