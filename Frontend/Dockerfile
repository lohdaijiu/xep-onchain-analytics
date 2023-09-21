FROM python:3.8-slim-buster

COPY webapp/requirements.txt .
RUN pip install -r requirements.txt

COPY webapp/ ./

EXPOSE 80

CMD [ "gunicorn", "-b 0.0.0.0:80", "application:application"]