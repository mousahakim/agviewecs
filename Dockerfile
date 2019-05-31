FROM python:2.7

RUN apt-get update && apt-get install -y && pip install uwsgi && pip install redis==2.10.6

WORKDIR /app/agviewer

COPY . /app

RUN pip install --trusted-host pypi.python.org -r ../requirements.txt

EXPOSE 80

CMD ["celery", "-A", "morph2o", "worker", "-n", "@%h", "--max-tasks-per-child=1"]
