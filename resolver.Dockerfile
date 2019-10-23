FROM python:3.7-slim-buster

RUN pip install pip==19.3.1

COPY /requirements/resolver.txt /tmp/requirements.txt

RUN pip install -r /tmp/requirements.txt

COPY /redirect_resolver /code/redirect_resolver

WORKDIR /code/

ENV PYTHONPATH=/code/
ENTRYPOINT ["python", "-m", "redirect_resolver"]
