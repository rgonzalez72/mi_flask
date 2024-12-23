FROM python:3.8-slim-buster


COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt

WORKDIR /python-docker

CMD ["python3", "-m", "flask", "run", "--debug", "--host=0.0.0.0"]
